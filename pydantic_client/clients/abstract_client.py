from typing import Any, Dict, Tuple

from pydantic_client.schema.http_request import HttpRequest


class AbstractClient:

    def do_request(
        self, request: HttpRequest,
    ) -> Any:
        raise NotImplementedError

    @staticmethod
    def parse_request(request: HttpRequest) -> Tuple[Dict, Dict]:
        if request.data:
            data = request.data
            json = {}
        else:
            data = {}
            json = request.json_body
        return data, json
