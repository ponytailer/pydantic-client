from typing import Any, Dict, Tuple, Callable

from pydantic_client.schema.http_request import HttpRequest


class AbstractClient:
    @staticmethod
    def data_encoder(x):
        return x

    def do_request(self, request: HttpRequest) -> Any:
        raise NotImplementedError

    @staticmethod
    def parse_request(request: HttpRequest) -> Tuple[Dict, Dict]:
        if request.data:
            data = request.data
            json = None
        else:
            data = None
            json = request.json_body
        return data, json
