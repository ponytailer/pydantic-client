import inspect
from typing import Any, Callable, Dict, Type

from pydantic_client.schema.method_info import MethodInfo


def create_response_type(annotations: Dict[str, Any]) -> Type:
    return annotations.pop("return", Any)


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
        response_type=create_response_type(annotations),
        form_body=form_body
    )
