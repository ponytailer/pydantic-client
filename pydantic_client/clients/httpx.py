from typing import Any

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

    async def do_request(self, request: HttpRequest) -> Any:
        async with self.get_session() as session:
            try:
                response = await session.request(**self.parse(request))
                response.raise_for_status()
                if response.is_success:
                    if not request.is_file:
                        return response.json()
                    return response.read()
            except BaseException as e:
                raise e
