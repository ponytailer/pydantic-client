from typing import Any, Type
from urllib.parse import urljoin

from aiohttp.client import ClientSession

from pydantic_client.clients.abstract_client import AbstractClient
from pydantic_client.proxy import AsyncClientProxy, Proxy
from pydantic_client.schema.http_request import HttpRequest


class AIOHttpClient(AbstractClient):
    runner_class: Type[Proxy] = AsyncClientProxy

    def __init__(self, base_url: str, session: ClientSession = ClientSession()):
        self.session = session
        self.base_url = base_url

    async def do_request(self, request: HttpRequest) -> Any:
        data, json = self.parse_request(request)
        async with self.session as session:
            try:
                req = session.request(
                    url=urljoin(self.base_url, request.url),
                    method=request.method,
                    json=json,
                    data=data
                )

                async with req as resp:
                    resp.raise_for_status()
                    if resp.status == 200:
                        return resp.json()
            except BaseException as e:
                raise e
