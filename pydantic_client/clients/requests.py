from typing import Any

from pydantic_client.clients.abstract_client import AbstractClient
from pydantic_client.schema.http_request import HttpRequest

try:
    from requests import Session
except ImportError:
    raise ImportError("Please install `requests` to use RequestsClient")


class RequestsClient(AbstractClient):
    session = Session()

    def do_request(self, request: HttpRequest) -> Any:
        data, json = self.parse_request(request)
        headers = request.request_headers if request.request_headers \
            else self.config.headers

        try:
            return self.session.request(
                url=self.base_url + request.url,
                method=request.method,
                json=json,
                data=data,
                headers=headers,
                timeout=self.config.timeout,
            ).json()
        except BaseException as e:
            raise e
