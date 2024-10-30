from typing import Any, Dict

from pydantic_client.schema.client_config import ClientConfig
from pydantic_client.schema.http_request import HttpRequest


class AbstractClient:

    def __init__(self, config: ClientConfig):
        self.config = config
        self.base_url = config.base_url.rstrip("/")

    def get_session(self):
        return self.config.client_session

    def do_request(self, request: HttpRequest) -> Any:
        raise NotImplementedError

    def parse(self, request: HttpRequest) -> Dict[str, Any]:
        if request.data:
            data, json = request.data, None
        else:
            data, json = None, request.json_body
        headers = request.request_headers if request.request_headers \
            else self.config.headers
        url = self.base_url + request.url
        return dict(url=url, data=data, json=json, headers=headers,
                    method=request.method, timeout=self.config.timeout)

    @classmethod
    def from_toml(cls, toml_config: ClientConfig):
        return cls(toml_config)
