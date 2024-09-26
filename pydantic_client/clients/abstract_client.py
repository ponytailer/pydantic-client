from typing import Any, Dict, Tuple, Optional

from pydantic_client.schema.client_config import ClientConfig
from pydantic_client.schema.http_request import HttpRequest


class AbstractClient:

    def __init__(self, config: ClientConfig):
        self.config = config
        self.base_url = config.base_url.rstrip("/")

    def do_request(self, request: HttpRequest) -> Any:
        raise NotImplementedError

    @staticmethod
    def parse_request(request: HttpRequest) -> Tuple[Dict, Dict]:
        if request.data:
            data, json = request.data, None
        else:
            data, json = None, request.json_body
        return data, json

    @classmethod
    def from_toml(cls, toml_config: ClientConfig):
        return cls(toml_config)
