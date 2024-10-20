from typing import Any, Callable

from pydantic_client.clients.abstract_client import AbstractClient
from pydantic_client.schema.http_request import HttpRequest

try:
    from aiohttp.client import ClientSession
except ImportError:
    raise ImportError("Please install `aiohttp` to use AIOHttpClient")


class AIOHttpClient(AbstractClient):

    def get_session(self) -> Callable[[], ClientSession]:
        session = super().get_session()
        return lambda: ClientSession() if not session else session()

    async def do_request(self, request: HttpRequest) -> Any:
        data, json = self.parse_request(request)
        headers = request.request_headers if request.request_headers \
            else self.config.headers

        session_factory = self.get_session()
        s = session_factory()
        async with s as session:
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
