from typing import Any, Dict, Optional, Type, TypeVar

import aiohttp
from pydantic import BaseModel

from .base import BaseWebClient

T = TypeVar('T', bound=BaseModel)


class AiohttpWebClient(BaseWebClient):
    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        response_model: Optional[Type[T]] = None
    ) -> Any:
        url = self._make_url(path)

        async with aiohttp.ClientSession() as session:
            async with session.request(
                method=method,
                url=url,
                params=params,
                json=json,
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                response.raise_for_status()
                data = await response.json()

                if response_model is not None:
                    return response_model.parse_obj(data)
                return data


class HttpxWebClient(BaseWebClient):
    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        response_model: Optional[Type[T]] = None
    ) -> Any:
        import httpx
        url = self._make_url(path)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method=method,
                url=url,
                params=params,
                json=json,
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()

            if response_model is not None:
                return response_model.parse_obj(data)
            return data
