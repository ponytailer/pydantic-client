from typing import Any, Dict, Optional, Type, TypeVar

import requests
from pydantic import BaseModel

from .base import BaseWebClient

T = TypeVar('T', bound=BaseModel)


class RequestsWebClient(BaseWebClient):
    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] =30,
        session: Optional[requests.Session] = None
    ):
        super().__init__(base_url, headers, timeout)
        if not self.session:
            self.session = requests.Session()

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
        
        # Merge headers
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        response = requests.request(
            method=method,
            url=url,
            params=params,
            json=json,
            data=data,
            headers=request_headers,
            timeout=self.timeout
        )
        response.raise_for_status()

        data = response.json()
        if response_model is not None:
            return response_model.model_validate(data)
        return data
