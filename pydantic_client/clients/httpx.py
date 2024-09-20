from typing import Any, Type

from httpx import AsyncClient
from pydantic_client.clients.abstract_client import AbstractClient
from pydantic_client.proxy import AsyncClientProxy, Proxy
from pydantic_client.schema.http_request import HttpRequest


class HttpxClient(AbstractClient):
    runner_class: Type[Proxy] = AsyncClientProxy

    async def do_request(self, request: HttpRequest) -> Any:
        data, json = self.parse_request(request)
        headers = request.request_headers if request.request_headers \
            else self.headers
        async with AsyncClient(http2=self.http2) as session:
            try:
                response = await session.request(
                    url=self.base_url + request.url,
                    method=request.method,
                    json=json,
                    data=data,
                    headers=headers
                )
                response.raise_for_status()
                if response.is_success:
                    return response.json()
            except BaseException as e:
                raise e
