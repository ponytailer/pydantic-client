from typing import Any, Type, Dict

from aiohttp.client import ClientSession

from pydantic_client.clients.abstract_client import AbstractClient
from pydantic_client.proxy import AsyncClientProxy, Proxy
from pydantic_client.schema.http_request import HttpRequest


class AIOHttpClient(AbstractClient):
    runner_class: Proxy = AsyncClientProxy

    def __init__(self, base_url: str, headers: Dict[str, Any] = None):
        self.base_url = base_url.rstrip("/")
        self.headers = headers

    async def do_request(self, request: HttpRequest) -> Any:
        data, json = self.parse_request(request)
        headers = request.request_headers if request.request_headers \
            else self.headers
        async with ClientSession() as session:
            try:
                req = session.request(
                    url=self.base_url + request.url,
                    method=request.method,
                    json=json,
                    data=data,
                    headers=headers
                )

                async with req as resp:
                    resp.raise_for_status()
                    if resp.status == 200:
                        return await resp.json()
            except BaseException as e:
                raise e
