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
        response_model: Optional[Type[T]] = None
    ) -> Any:
        url = self._make_url(path)

        response = requests.request(
            method=method,
            url=url,
            params=params,
            json=json,
            headers=self.headers,
            timeout=self.timeout
        )
        response.raise_for_status()

        data = response.json()
        if response_model is not None:
            return response_model.parse_obj(data)
        return data
