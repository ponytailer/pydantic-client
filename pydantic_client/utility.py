import inspect
from typing import Any, Callable, Dict, Optional, Type

from pydantic import BaseModel

from pydantic_client.schema.method_info import MethodInfo


def create_response_type(annotations: Dict[str, Any]) -> Optional[Type]:
    response_type = annotations.pop("return", None)
    if response_type is None:
        return response_type

    class T(BaseModel):
        val: response_type

    return T


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
