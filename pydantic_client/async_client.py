from typing import Any, Dict, Optional, TypeVar

from pydantic import BaseModel

from .base import BaseWebClient, RequestInfo

try:
    import aiohttp
except ImportError:
    raise ImportError("please install aiohttp: `pip install aiohttp`")


T = TypeVar('T', bound=BaseModel)


class AiohttpWebClient(BaseWebClient):
    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] =30,
        session: Optional[aiohttp.ClientSession] = None,
        statsd_address: Optional[str] = None
    ):
        super().__init__(base_url, headers, timeout, session, statsd_address)

    async def _request(self, request_info: RequestInfo) -> Any:
        request_params = self.dump_request_params(request_info)
        response_model = request_params.pop("response_model")

        request_params = self.before_request(request_params)

        async with aiohttp.ClientSession() as session:
            async with session.request(
                **request_params,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                response.raise_for_status()
                data = await response.json()

                if response_model is not None:
                    return response_model.model_validate(data, from_attributes=True)
                return data


class HttpxWebClient(BaseWebClient):

    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] =30,
        session = None,
        statsd_address: Optional[str] = None
    ):
        super().__init__(base_url, headers, timeout, session, statsd_address)
        try:
            import httpx
        except ImportError:
            raise ImportError("please install httpx: `pip install httpx`")

    async def _request(self, request_info: RequestInfo) -> Any:
        import httpx
        request_params = self.dump_request_params(request_info)
        response_model = request_params.pop("response_model")

        request_params = self.before_request(request_params)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(**request_params)
            response.raise_for_status()
            data = response.json()
            if response_model is not None:
                return response_model.model_validate(data, from_attributes=True)
            return data
