from typing import Any

from pydantic_client.clients.abstract_client import AbstractClient
from pydantic_client.schema.http_request import HttpRequest

try:
    from requests import Session
except ImportError:
    raise ImportError("Please install `requests` to use RequestsClient")


class RequestsClient(AbstractClient):
    session = Session()

    def get_session(self) -> Session:
        session = super().get_session()
        return session if isinstance(session, Session) else self.session

    def do_request(self, request: HttpRequest) -> Any:
        try:
            response = self.get_session().request(**self.parse(request))
            response.raise_for_status()
            return response.json() if not request.is_file else response.content
        except BaseException as e:
            raise e
