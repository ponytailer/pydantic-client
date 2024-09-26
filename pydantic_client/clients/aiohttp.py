from typing import Any

from aiohttp.client import ClientSession

from pydantic_client.clients.abstract_client import AbstractClient
from pydantic_client.schema.http_request import HttpRequest


class AIOHttpClient(AbstractClient):

    async def do_request(self, request: HttpRequest) -> Any:
        data, json = self.parse_request(request)
        headers = request.request_headers if request.request_headers \
            else self.config.headers
        async with ClientSession() as session:
            try:
                req = session.request(
                    url=self.base_url + request.url,
                    method=request.method,
                    json=json,
                    data=data,
                    headers=headers,
                    timeout=self.config.timeout
                )

                async with req as resp:
                    resp.raise_for_status()
                    if resp.status == 200:
                        return await resp.json()
            except BaseException as e:
                raise e
