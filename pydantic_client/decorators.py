import inspect
import re
import warnings
from functools import wraps
from typing import Callable, Optional, Literal

from pydantic import BaseModel

from .base import PydanticClientValidationError
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
        static_qs = []
        for pair in query.split('&'):
            if '=' in pair:
                k, v = pair.split('=', 1)
                m = re.fullmatch(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}", v)
                if m:
                    # add dynamic qs
                    query_tpls.append((k, m.group(1)))
                else:
                    # add static qs
                    static_qs.append((k, v))

        return path_template, query_tpls, static_qs
    else:
        return path, [], []

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
    func: Callable, method: str, path: str, form_body: bool, response_extract_path: Optional[str] = None,
    unknown_args_behavior: Literal['query', 'body', 'not_allow'] = 'body', *args, **kwargs
) -> RequestInfo:
    sig = inspect.signature(func)
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()
    params = dict(bound_args.arguments)
    params.pop("self", None)
    request_headers = params.pop("request_headers", None)

    response_model = sig.return_annotation
    if isinstance(response_model, str):
        response_model = eval(response_model)

    raw_path, query_tpls, static_qs = _extract_path_and_query(path)

    used_in_path_params = []
    format_path_data = {}
    for k in re.findall(r'{([a-zA-Z_][a-zA-Z0-9_]*)}', raw_path):
        format_path_data[k] = params[k]
        used_in_path_params.append(k)
    formatted_path = raw_path.format(**format_path_data)

    query_params = {}
    # fill static qs
    for k, v in static_qs:
        query_params[k] = v

    # fill dynamic qs with overwrite
    for k, v_name in query_tpls:
        v = params.pop(v_name, None)
        if v is not None:
            query_params[k] = v

    # if param used in path, but not used in query_string
    # need for support overlap test with path `/{keyword}?kw={keyword}`
    # and correct unknown_args_behavior=not_allow
    for k in used_in_path_params:
        if k in params:
            del params[k]

    body_data = None
    for param_name, param_value in params.copy().items():
        if isinstance(param_value, BaseModel):
            # rewrite body_data twice (or more) not allowed
            if body_data is not None:
                raise PydanticClientValidationError(f'Cannot put multiple data objects in request')

            if method in ["POST", "PUT", "PATCH"]:
                # pydantic.Field(serialization_alias=...) works only with by_alias=True
                body_data = param_value.model_dump(mode='json', by_alias=True)

                # removing used params from variable
                del params[param_name]
            else:
                raise PydanticClientValidationError(f'Cannot put body data in {method} request')

    if params:
        # raise if params have non-used variables (probably error in path {var1} with arg another name)
        # example: path = '/?qs_dynamic={qs_11111}' with arg name 'qs_dynamic'
        # aka strict mode
        if unknown_args_behavior == 'not_allow':
            raise PydanticClientValidationError('Some arguments is not filled, verify path and func argument names')

        if unknown_args_behavior == 'query':
            query_params.update(params)

        if unknown_args_behavior == 'body':
            if body_data is not None:
                raise PydanticClientValidationError(f'Cannot fill body because is not empty')
            body_data = params

    info = {
        "method": method,
        "path": formatted_path,
        "params": query_params, # all request methods can have query_params
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
    return RequestInfo.model_validate(info, by_alias=True)

def rest(
    method: str, 
    form_body: bool = False,
    agno_tool: bool = False,
    tool_description: Optional[str] = None,
    response_extract_path: Optional[str] = None,
    unknown_args_behavior: Literal['query', 'body', 'not_allow'] = 'body'
) -> Callable:
    def decorator(path: str) -> Callable:
        def wrapper(func: Callable) -> Callable:
            _warn_if_path_params_missing(path, func)
            if agno_tool:
                func = register_agno_tool(tool_description)(func)

            @wraps(func)
            async def async_wrapped(self, *args, **kwargs):
                request_params = _process_request_params(
                    func, method, path, form_body, response_extract_path, unknown_args_behavior, self, *args, **kwargs
                )
                return await self._request(request_params)

            @wraps(func)
            def sync_wrapped(self, *args, **kwargs):
                request_params = _process_request_params(
                    func, method, path, form_body, response_extract_path, unknown_args_behavior, self, *args, **kwargs
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
    response_extract_path: Optional[str] = None,
    unknown_args_behavior: Literal['query', 'body', 'not_allow'] = 'body'
) -> Callable:
    return rest(
        "GET", 
        agno_tool=agno_tool, 
        tool_description=tool_description,
        response_extract_path=response_extract_path,
        unknown_args_behavior=unknown_args_behavior
    )(path)


def delete(
    path: str,
    agno_tool: bool = False,
    tool_description: Optional[str] = None,
    response_extract_path: Optional[str] = None,
    unknown_args_behavior: Literal['query', 'body', 'not_allow'] = 'body'
) -> Callable:
    return rest(
        "DELETE", 
        agno_tool=agno_tool, 
        tool_description=tool_description,
        response_extract_path=response_extract_path,
        unknown_args_behavior=unknown_args_behavior
    )(path)


def post(
    path: str,
    form_body: bool = False,
    agno_tool: bool = False,
    tool_description: Optional[str] = None,
    response_extract_path: Optional[str] = None,
    unknown_args_behavior: Literal['query', 'body', 'not_allow'] = 'body'
) -> Callable:
    return rest(
        "POST", 
        form_body=form_body,
        agno_tool=agno_tool, 
        tool_description=tool_description,
        response_extract_path=response_extract_path,
        unknown_args_behavior=unknown_args_behavior
    )(path)


def put(
    path: str,
    form_body: bool = False,
    agno_tool: bool = False,
    tool_description: Optional[str] = None,
    response_extract_path: Optional[str] = None,
    unknown_args_behavior: Literal['query', 'body', 'not_allow'] = 'body'
) -> Callable:
    return rest(
        "PUT", 
        form_body=form_body,
        agno_tool=agno_tool, 
        tool_description=tool_description,
        response_extract_path=response_extract_path,
        unknown_args_behavior=unknown_args_behavior
    )(path)


def patch(
    path: str,
    form_body: bool = False,
    agno_tool: bool = False,
    tool_description: Optional[str] = None,
    response_extract_path: Optional[str] = None,
    unknown_args_behavior: Literal['query', 'body', 'not_allow'] = 'body'
) -> Callable:
    return rest(
        "PATCH", 
        form_body=form_body,
        agno_tool=agno_tool, 
        tool_description=tool_description,
        response_extract_path=response_extract_path,
        unknown_args_behavior=unknown_args_behavior
    )(path)
