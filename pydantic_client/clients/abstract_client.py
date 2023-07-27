from typing import Any, Type

from pydantic_client.proxy import Proxy
from pydantic_client.schema.http_request import HttpRequest


class AbstractClient:
    runner_class: Type[Proxy]

    def do_request(
        self, request: HttpRequest,
    ) -> Any:
        raise NotImplementedError
