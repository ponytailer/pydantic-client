from typing import Any
from urllib.parse import urljoin

from aiohttp.client import ClientSession

from pydantic_client.clients.abstract_client import AbstractClient
from pydantic_client.proxy import AsyncClientProxy
from pydantic_client.schema.http_request import HttpRequest


class AIOHttpClient(AbstractClient):
    runner_class = AsyncClientProxy

    def __init__(self, base_url: str, session: ClientSession = ClientSession()):
        self.session = session
        self.base_url = base_url

    async def do_request(self, request: HttpRequest) -> Any:

        if request.data:
            data = request.data
            json = {}
        else:
            data = {}
            json = request.json_body

        async with self.session as session:
            try:
                req = session.post(
                    url=urljoin(self.base_url, request.url),
                    json=json,
                    data=data
                )

                async with req as resp:
                    resp.raise_for_status()
                    if resp.status == 200:
                        return resp.json()
            except BaseException as e:
                raise e
