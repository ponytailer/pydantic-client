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
    Split path and querystring, and return:
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
    """Check if all {var} in path appear in func parameters during registration"""
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
    func: Callable, method: str, path: str, form_body: bool, response_extract_path: Optional[str] = None, *args, **kwargs
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
        response_model = return_type
    raw_path, query_tpls = _extract_path_and_query(path)

    formatted_path = raw_path.format(**{
        k: params[k] for k in re.findall(r'{([a-zA-Z_][a-zA-Z0-9_]*)}', raw_path)
    })

    query_params = {}
    for k, v_name in query_tpls:
        v = params.pop(v_name, None)
        if v is not None:
            query_params[k] = v
    
    body_data = None
    for param_name, param_value in params.items():
        if isinstance(param_value, BaseModel):
            if method in ["POST", "PUT", "PATCH"]:
                body_data = param_value.model_dump()

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
        "function_name": func.__name__,
        "response_extract_path": response_extract_path
    }
    return RequestInfo.model_validate(info)

def rest(
    method: str, 
    form_body: bool = False,
    agno_tool: bool = False,
    tool_description: Optional[str] = None,
    response_extract_path: Optional[str] = None
) -> Callable:
    def decorator(path: str) -> Callable:
        def wrapper(func: Callable) -> Callable:
            _warn_if_path_params_missing(path, func)
            if agno_tool:
                func = register_agno_tool(tool_description)(func)

            @wraps(func)
            async def async_wrapped(self, *args, **kwargs):
                request_params = _process_request_params(
                    func, method, path, form_body, response_extract_path, self, *args, **kwargs
                )
                return await self._request(request_params)

            @wraps(func)
            def sync_wrapped(self, *args, **kwargs):
                request_params = _process_request_params(
                    func, method, path, form_body, response_extract_path, self, *args, **kwargs
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


def get(
    path: str,
    agno_tool: bool = False,
    tool_description: Optional[str] = None,
    response_extract_path: Optional[str] = None
) -> Callable:
    return rest(
        "GET", 
        agno_tool=agno_tool, 
        tool_description=tool_description,
        response_extract_path=response_extract_path
    )(path)


def delete(
    path: str,
    agno_tool: bool = False,
    tool_description: Optional[str] = None,
    response_extract_path: Optional[str] = None
) -> Callable:
    return rest(
        "DELETE", 
        agno_tool=agno_tool, 
        tool_description=tool_description,
        response_extract_path=response_extract_path
    )(path)


def post(
    path: str,
    form_body: bool = False,
    agno_tool: bool = False,
    tool_description: Optional[str] = None,
    response_extract_path: Optional[str] = None
) -> Callable:
    return rest(
        "POST", 
        form_body=form_body,
        agno_tool=agno_tool, 
        tool_description=tool_description,
        response_extract_path=response_extract_path
    )(path)


def put(
    path: str,
    form_body: bool = False,
    agno_tool: bool = False,
    tool_description: Optional[str] = None,
    response_extract_path: Optional[str] = None
) -> Callable:
    return rest(
        "PUT", 
        form_body=form_body,
        agno_tool=agno_tool, 
        tool_description=tool_description,
        response_extract_path=response_extract_path
    )(path)


def patch(
    path: str,
    form_body: bool = False,
    agno_tool: bool = False,
    tool_description: Optional[str] = None,
    response_extract_path: Optional[str] = None
) -> Callable:
    return rest(
        "PATCH", 
        form_body=form_body,
        agno_tool=agno_tool, 
        tool_description=tool_description,
        response_extract_path=response_extract_path
    )(path)
