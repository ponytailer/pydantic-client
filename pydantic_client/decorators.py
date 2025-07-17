import inspect
import re
import warnings
from functools import wraps
from typing import Callable, Optional

from pydantic import BaseModel

from .tools.agno import register_agno_tool
from .schema import RequestInfo

def _extract_path_and_query(path: str):
    """
    拆分 path、querystring，并返回:
    - path_template: /users
    - query_tpls: [("name", "name"), ("age", "age")] for /users?name={name}&age={age}
    """
    if '?' in path:
        path_template, query = path.split('?', 1)
        query_tpls = []
        for pair in query.split('&'):
            if '=' in pair:
                k, v = pair.split('=', 1)
                m = re.fullmatch(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}", v)
                if m:
                    query_tpls.append((k, m.group(1)))

        return path_template, query_tpls
    else:
        return path, []

def _warn_if_path_params_missing(path: str, func: Callable):
    """注册时检查 path 中 {var} 是否都出现在 func 参数中"""
    sig = inspect.signature(func)
    func_params = set(sig.parameters) - {"self"}
    path_part = path.split('?', 1)[0]
    path_vars = set(re.findall(r'{([a-zA-Z_][a-zA-Z0-9_]*)}', path_part))
    missing = path_vars - func_params
    if missing:
        warnings.warn(
            f"Function '{func.__name__}' missing parameters {missing} required by path '{path}'"
        )

def _process_request_params(
    func: Callable, method: str, path: str, form_body: bool, *args, **kwargs
) -> RequestInfo:
    sig = inspect.signature(func)
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()
    params = dict(bound_args.arguments)
    params.pop("self", None)
    request_headers = params.pop("request_headers", None)
    return_type = sig.return_annotation

    if isinstance(return_type, type) and issubclass(return_type, BaseModel):
        response_model = return_type
    elif return_type in [str, bytes]:
        response_model = return_type
    else:
        response_model = None

    # 1. path/querystring 拆分
    raw_path, query_tpls = _extract_path_and_query(path)
    # 2. 渲染 path 参数（必须全部存在，否则format会KeyError，前面已warn过）
    formatted_path = raw_path.format(**{k: params[k] for k in re.findall(r'{([a-zA-Z_][a-zA-Z0-9_]*)}', raw_path)})
    # 3. 从 params 删除已用于 path 的
    # for k in re.findall(r'{([a-zA-Z_][a-zA-Z0-9_]*)}', raw_path):
        # params.pop(k, None)
    # 4. 处理 querystring 模板参数 —— 只有非None才加
    query_params = {}
    for k, v_name in query_tpls:
        v = params.pop(v_name, None)
        if v is not None:
            query_params[k] = v
    
    # 5. 剩余参数，GET/DELETE 做 query，POST/PUT/PATCH 做 body
    body_data = None
    for param_name, param_value in params.items():
        if isinstance(param_value, BaseModel):
            if method in ["POST", "PUT", "PATCH"]:
                body_data = param_value.model_dump()
        # else:
            # if method in ["GET", "DELETE"]:
                # if param_value is not None:
                    # query_params[param_name] = param_value

    info = {
        "method": method,
        "path": formatted_path,
        "params": query_params if method in ["GET", "DELETE"] else None,
        "json": (
            body_data
            if not form_body and method in ["POST", "PUT", "PATCH"]
            else None
        ),
        "data": (
            body_data
            if form_body and method in ["POST", "PUT", "PATCH"]
            else None
        ),
        "headers": request_headers,
        "response_model": response_model,
    }
    return RequestInfo.model_validate(info)

def rest(
    method: str, 
    form_body: bool = False,
    agno_tool: bool = False,
    tool_description: Optional[str] = None
) -> Callable:
    def decorator(path: str) -> Callable:
        def wrapper(func: Callable) -> Callable:
            _warn_if_path_params_missing(path, func)
            if agno_tool:
                func = register_agno_tool(tool_description)(func)

            @wraps(func)
            async def async_wrapped(self, *args, **kwargs):
                request_params = _process_request_params(
                    func, method, path, form_body, self, *args, **kwargs
                )
                return await self._request(request_params)

            @wraps(func)
            def sync_wrapped(self, *args, **kwargs):
                request_params = _process_request_params(
                    func, method, path, form_body, self, *args, **kwargs
                )
                return self._request(request_params)

            @wraps(func)
            def choose_wrapper(self, *args, **kwargs):
                if inspect.iscoroutinefunction(self._request):
                    return async_wrapped(self, *args, **kwargs)
                return sync_wrapped(self, *args, **kwargs)

            return choose_wrapper

        return wrapper

    return decorator

get = rest("GET")
delete = rest("DELETE")

def post(path: str, form_body: bool = False) -> Callable:
    return rest("POST", form_body=form_body)(path)

def put(path: str, form_body: bool = False) -> Callable:
    return rest("PUT", form_body=form_body)(path)

def patch(path: str, form_body: bool = False) -> Callable:
    return rest("PATCH", form_body=form_body)(path)
