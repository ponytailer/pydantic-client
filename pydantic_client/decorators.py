import inspect
import logging
from functools import partial, wraps
from typing import Callable

from pydantic._internal._model_construction import ModelMetaclass

from pydantic_client.container import container
from pydantic_client.schema.file import File
from pydantic_client.schema.method_info import MethodInfo

logger = logging.getLogger(__name__)


def parse_func(
    *,
    url: str,
    func: Callable,
    method: str,
    form_body: bool,
):
    spec = inspect.getfullargspec(func)
    annotations = spec.annotations.copy()
    return MethodInfo(
        func=func,
        http_method=method,
        url=url,
        request_type=annotations,
        response_type=annotations.pop("return", None),
        form_body=form_body
    )


def rest(
    url,
    method: str = "GET",
    form_body: bool = False
) -> Callable:
    if not url.startswith("/"):
        raise ValueError("url must start with slash.")

    def wrapper(func: Callable):
        method_info = parse_func(
            url=url,
            func=func,
            method=method,
            form_body=form_body
        )
        container.bind_func(func, method_info)

        def convert(value, target_type):
            rt = method_info.response_type
            if not rt:
                return value
            if isinstance(rt, File) and isinstance(value, bytes):
                return value
            if isinstance(rt, ModelMetaclass):
                return target_type.model_validate(value, from_attributes=True)
            try:
                return target_type(value)
            except Exception as e:
                logger.warning(
                    f"Failed to convert {value} to {target_type}: {e}")
                return value

        @wraps(func)
        async def async_wrapped_func(*args, **kwargs):
            ret = container.do_func(func, *args, **kwargs)
            if inspect.isawaitable(ret):
                ret = await ret
            return convert(ret, method_info.response_type)

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            ret = container.do_func(func, *args, **kwargs)
            return convert(ret, method_info.response_type)

        return async_wrapped_func if (
            inspect.iscoroutinefunction(func)) else wrapped_func

    return wrapper


get = partial(rest, method="GET")
post = partial(rest, method="POST")
delete = partial(rest, method="DELETE")
put = partial(rest, method="PUT")
patch = partial(rest, method="PATCH")
