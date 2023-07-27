from functools import partial
from typing import Callable

from pydantic_client.schema.method_info import MethodInfo
from pydantic_client.utility import parse_func


def rest(
    url,
    method: str = "GET",
    form_body: bool = False
) -> Callable:
    def wrapper(func: Callable) -> MethodInfo:
        return parse_func(
            url=url,
            func=func,
            method=method,
            form_body=form_body
        )

    return wrapper


get = partial(rest, method="GET")
post = partial(rest, method="POST")
delete = partial(rest, method="DELETE")
put = partial(rest, method="PUT")
