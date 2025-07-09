import inspect
from functools import wraps, partial
from typing import Callable, TypeVar

from pydantic import BaseModel

from .schema.argument import RequestData, RequestParameters, PathInfo, \
    ResponseTypeInfo
from .schema.file import File

T = TypeVar('T')


def _process_parameters(func: Callable, args: tuple,
    kwargs: dict) -> RequestParameters:
    """处理函数参数并提取 headers"""
    sig = inspect.signature(func)
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()
    params = dict(bound_args.arguments)
    request_headers = params.pop('request_headers', None)
    params.pop('self', None)
    return RequestParameters(
        params=params,
        headers=request_headers
    )


def _process_path_params(path: str, params: dict) -> PathInfo:
    """处理路径参数并返回格式化的路径"""
    params = params.copy()
    formatted_path = path.format(**params)

    # Remove path parameters
    for key in path.split('{')[1:]:
        key = key.split('}')[0]
        params.pop(key, None)

    return PathInfo(
        formatted_path=formatted_path,
        remaining_params=params
    )


def _process_request_params(method: str, params: dict,
    form_body: bool) -> RequestData:
    """处理请求参数，返回查询参数和请求体"""
    body_data = None
    query_params = {}

    for param_name, param_value in params.items():
        if isinstance(param_value, BaseModel):
            if method in ['POST', 'PUT', 'PATCH']:
                body_data = param_value.model_dump()
        else:
            if method in ['GET', 'DELETE']:
                query_params[param_name] = param_value

    return RequestData(
        query_params=query_params if method in ['GET', 'DELETE'] else None,
        json_data=body_data if not form_body and method in ['POST', 'PUT',
                                                            'PATCH'] else None,
        form_data=body_data if form_body and method in ['POST', 'PUT',
                                                        'PATCH'] else None
    )


def _get_response_type(func: Callable) -> ResponseTypeInfo:
    """获取响应类型信息"""
    return_type = inspect.signature(func).return_annotation
    response_model = None
    is_file_response = False

    if return_type in (bytes, str, File):
        is_file_response = True
    elif isinstance(return_type, type) and issubclass(return_type, BaseModel):
        response_model = return_type

    return ResponseTypeInfo(
        response_model=response_model,
        is_file_response=is_file_response,
        return_type=return_type
    )


def rest(method: str, form_body: bool = False):
    def decorator(path: str):
        if not path.startswith("/"):
            raise ValueError("url must start with slash.")

        def wrapper(func: Callable):
            @wraps(func)
            async def async_wrapped(self, *args, **kwargs):
                # Process parameters with Pydantic models
                req_params = _process_parameters(func, args, kwargs)
                path_info = _process_path_params(path, req_params.params)
                req_data = _process_request_params(method,
                                                   path_info.remaining_params,
                                                   form_body)
                resp_type = _get_response_type(func)

                # Make request
                return await self._request(
                    method=method,
                    path=path_info.formatted_path,
                    params=req_data.query_params,
                    json=req_data.json_data,
                    data=req_data.form_data,
                    headers=req_params.headers,
                    response_model=resp_type.response_model
                )

            @wraps(func)
            def sync_wrapped(self, *args, **kwargs):
                # Process parameters with Pydantic models
                req_params = _process_parameters(func, args, kwargs)
                path_info = _process_path_params(path, req_params.params)
                req_data = _process_request_params(method,
                                                   path_info.remaining_params,
                                                   form_body)
                resp_type = _get_response_type(func)

                return self._request(
                    method=method,
                    path=path_info.formatted_path,
                    params=req_data.query_params,
                    json=req_data.json_data,
                    data=req_data.form_data,
                    headers=req_params.headers,
                    response_model=resp_type.response_model
                )

            def choose_wrapper(self, *args, **kwargs):
                if inspect.iscoroutinefunction(self._request):
                    return async_wrapped(self, *args, **kwargs)
                return sync_wrapped(self, *args, **kwargs)

            return choose_wrapper

        return wrapper

    return decorator


get = partial(rest, "GET")
post = partial(rest, "POST")
put = partial(rest, "PUT")
patch = partial(rest, "PATCH")
delete = partial(rest, "DELETE")
