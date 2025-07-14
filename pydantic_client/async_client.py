from typing import Any, Dict, Optional, Type, TypeVar

from pydantic import BaseModel

from .base import BaseWebClient

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
        session: Optional[aiohttp.ClientSession] = None
    ):
        super().__init__(base_url, headers, timeout)

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        response_model: Optional[Type[T]] = None
    ) -> Any:
        url = self._make_url(path)
        
        # Merge headers
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        async with aiohttp.ClientSession() as session:
            async with session.request(
                method=method,
                url=url,
                params=params,
                json=json,
                data=data,
                headers=request_headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                response.raise_for_status()
                data = await response.json()

                if response_model is not None:
                    return response_model.model_validate(data)
                return data


class HttpxWebClient(BaseWebClient):

    def __init__(self, base_url, headers = None, timeout = 30):
        super().__init__(base_url, headers, timeout)

        try:
            import httpx
        except ImportError:
            raise ImportError("please install httpx: `pip install httpx`")

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        response_model: Optional[Type[T]] = None
    ) -> Any:
        import httpx
        url = self._make_url(path)
        
        # Merge headers
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method=method,
                url=url,
                params=params,
                json=json,
                data=data,
                headers=request_headers
            )
            response.raise_for_status()
            data = response.json()

            if response_model is not None:
                return response_model.model_validate(data)
            return data
