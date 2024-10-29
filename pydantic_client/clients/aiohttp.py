from typing import Any, Callable, Dict

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

    async def do_request(self, request: HttpRequest) -> Dict[str, Any]:
        session_factory = self.get_session()
        s = session_factory()
        async with s as session:
            try:
                req = session.request(**self.parse(request))
                async with req as resp:
                    resp.raise_for_status()
                    if resp.status == 200:
                        return await resp.json()
            except BaseException as e:
                raise e
