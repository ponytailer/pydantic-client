from typing import Any, Dict, Optional, TypeVar
import logging

from pydantic import BaseModel

from .base import BaseWebClient, RequestInfo

logger = logging.getLogger(__name__)

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
        # Check if there's a mock response for this method
        mock_response = self._get_mock_response(request_info)
        if mock_response:
            return mock_response

        import aiohttp
        request_params = self.dump_request_params(request_info)
        response_model = request_params.pop("response_model")

        request_params = self.before_request(request_params)

        if not self.session:
            self.session = aiohttp.ClientSession()

        async with self.session.request(**request_params) as response:
            response.raise_for_status()

            if response_model is str:
                return await response.text()
            elif response_model is bytes:
                return await response.content.read()
            elif not response_model:
                return await response.json()
            return response_model.model_validate(await response.json(), from_attributes=True)


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
        # Check if there's a mock response for this method
        mock_response = self._get_mock_response(request_info)
        if mock_response:
            return mock_response
            
        # 没有mock数据，继续进行正常请求
        import httpx
        request_params = self.dump_request_params(request_info)
        response_model = request_params.pop("response_model")

        request_params = self.before_request(request_params)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(**request_params)
            response.raise_for_status()

            if response_model is str:
                return response.text
            elif response_model is bytes:
                return response.content
            elif not response_model:
                return response.json()
            return response_model.model_validate(response.json(), from_attributes=True)
