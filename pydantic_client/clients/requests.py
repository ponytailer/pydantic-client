from typing import Any, Dict, Type

from requests import Session

from pydantic_client.clients.abstract_client import AbstractClient
from pydantic_client.proxy import ClientProxy, Proxy
from pydantic_client.schema.http_request import HttpRequest


class RequestsClient(AbstractClient):
    runner_class: Type[Proxy] = ClientProxy

    def __init__(self, base_url: str, session: Session = Session(),
                 headers: Dict[str, Any] = None):
        self.session = session
        self.base_url = base_url.rstrip("/")
        self.headers = headers

    def do_request(self, request: HttpRequest) -> Any:
        data, json = self.parse_request(request)
        headers = request.request_headers if request.request_headers \
            else self.headers

        try:
            return self.session.request(
                url=self.base_url + request.url,
                method=request.method,
                json=json,
                data=data,
                headers=headers
            ).json()
        except BaseException as e:
            raise e
