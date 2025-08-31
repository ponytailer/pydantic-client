import logging
from typing import Any, Dict, Optional, Callable, AsyncIterator, Union

from pydantic import BaseModel

from .async_client import HttpxWebClient, RequestInfo

try:
    import httpx
except ImportError:
    raise ImportError("please install httpx: `pip install httpx`")


logger = logging.getLogger(__name__)


class StreamClient(HttpxWebClient):
    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = 30,
        session: Any = None,
        statsd_address: Optional[str] = None
    ):
        super().__init__(base_url, headers, timeout, session, statsd_address)
        try:
            import httpx
        except ImportError:
            raise ImportError(
                "please install httpx: `pip install httpx[http2]`")

    def _request(self, request_info: RequestInfo) -> Any:
        ...

    def _stream_request(
        self,
        request_info: RequestInfo,
        encoder: Optional[Callable[[str], ...]] = None
    ) -> Any:

        request_params = self.dump_request_params(request_info)
        request_params.pop("response_model", None)

        request_params = self.before_request(request_params)

        with httpx.Client(timeout=self.timeout) as client:
            with client.stream(**request_params) as response:
                response.raise_for_status()

                for chunk in response.iter_lines():
                    if chunk:
                        yield encoder(chunk) if encoder else chunk

    async def _async_stream_request(
        self,
        request_info: RequestInfo,
        encoder: Optional[Callable[[str], ...]] = None
    ) -> Any:
        request_params = self.dump_request_params(request_info)
        request_params.pop("response_model", None)

        request_params = self.before_request(request_params)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(**request_params) as response:
                response.raise_for_status()

                async for chunk in response.aiter_lines():
                    if chunk:
                        yield encoder(chunk) if encoder else chunk
