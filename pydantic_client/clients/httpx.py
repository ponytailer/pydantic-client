from typing import Any, Dict

from pydantic_client.clients.abstract_client import AbstractClient
from pydantic_client.schema.http_request import HttpRequest

try:
    from httpx import AsyncClient
except ImportError:
    raise ImportError("Please install `httpx` to use HttpxClient")


class HttpxClient(AbstractClient):

    def get_session(self):
        session = super().get_session()
        return session if isinstance(session, AsyncClient) \
            else AsyncClient(http2=self.config.http2)

    async def do_request(self, request: HttpRequest) -> Dict[str, Any]:
        async with self.get_session() as session:
            try:
                response = await session.request(**self.parse(request))
                response.raise_for_status()
                if response.is_success:
                    return response.json()
            except BaseException as e:
                raise e
