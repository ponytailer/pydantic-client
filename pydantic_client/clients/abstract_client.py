from typing import Any, Dict, Tuple

from pydantic_client.schema.ClientConfig import ClientConfig
from pydantic_client.schema.http_request import HttpRequest


class AbstractClient:

    def __init__(
        self, base_url: str, headers: Dict[str, Any] = None,
        http2: bool = False
    ):
        self.base_url = base_url.rstrip("/")
        self.headers = headers
        self.http2 = http2

    @staticmethod
    def data_encoder(x):
        return x

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
        return cls(**toml_config.model_dump())
