from typing import Any, Dict, Optional, Type, TypeVar

import requests
from pydantic import BaseModel

from .base import BaseWebClient

T = TypeVar('T', bound=BaseModel)


class RequestsWebClient(BaseWebClient):
    def _request(
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

        # Merge headers from client and request
        merged_headers = self.headers.copy()
        if headers:
            merged_headers.update(headers)

        response = requests.request(
            method=method,
            url=url,
            params=params,
            json=json,
            data=data,
            headers=merged_headers,
            timeout=self.timeout
        )
        response.raise_for_status()

        data = response.json()
        if response_model is not None:
            return response_model.model_validate(data)
        return data
