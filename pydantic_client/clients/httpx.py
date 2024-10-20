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
        if session and isinstance(session, AsyncClient):
            return session
        return AsyncClient(http2=self.config.http2)

    async def do_request(self, request: HttpRequest) -> Any:
        data, json = self.parse_request(request)
        headers = request.request_headers if request.request_headers \
            else self.config.headers

        async with self.get_session() as session:
            try:
                response = await session.request(
                    url=self.base_url + request.url,
                    method=request.method,
                    json=json,
                    data=data,
                    headers=headers,
                    timeout=self.config.timeout
                )
                response.raise_for_status()
                if response.is_success:
                    return response.json()
            except BaseException as e:
                raise e
