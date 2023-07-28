from typing import Any
from urllib.parse import urljoin

from requests import Session

from pydantic_client.clients.abstract_client import AbstractClient
from pydantic_client.proxy import ClientProxy
from pydantic_client.schema.http_request import HttpRequest


class RequestsClient(AbstractClient):

    runner_class = ClientProxy

    def __init__(self, base_url: str, session: Session = Session()):
        self.session = session
        self.base_url = base_url

    def do_request(self, request: HttpRequest) -> Any:
        if request.data:
            data = request.data
            json = {}
        else:
            data = {}
            json = request.json_body

        try:
            return self.session.request(
                url=urljoin(self.base_url, request.url),
                method=request.method,
                json=json,
                data=data,
            )
        except BaseException as e:
            raise e
