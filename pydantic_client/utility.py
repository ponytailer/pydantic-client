import inspect
from typing import Any, Callable, Type

from pydantic_client.schema.method_info import MethodInfo


def create_response_type(
    spec: inspect.FullArgSpec,
) -> Type:
    return spec.annotations.get("return", Any)


def parse_func(
    *,
    url: str,
    func: Callable,
    method: str,
    form_body: bool,
):

    spec = inspect.getfullargspec(func)

    return MethodInfo(
        func=func,
        http_method=method,
        url=url,
        request_type=spec.annotations,
        response_type=create_response_type(spec),
        form_body=form_body
    )
