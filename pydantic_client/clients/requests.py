from typing import Any, Dict

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

    def do_request(self, request: HttpRequest) -> Dict[str, Any]:
        try:
            return self.get_session().request(**self.parse(request)).json()
        except BaseException as e:
            raise e
