from typing import Any

from pydantic_client.schema.http_request import HttpRequest


class AbstractClient:

    def do_request(
        self, request: HttpRequest,
    ) -> Any:
        raise NotImplementedError
