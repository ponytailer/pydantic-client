from typing import Any, Dict, Optional, TypeVar

import requests
from pydantic import BaseModel

from .base import BaseWebClient, RequestInfo

T = TypeVar('T', bound=BaseModel)


class RequestsWebClient(BaseWebClient):
    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] =30,
        session: Optional[requests.Session] = None,
        statsd_address: Optional[str] = None
    ):
        super().__init__(base_url, headers, timeout, session, statsd_address)
        if not self.session:
            self.session = requests.Session()

    def _request(self, request_info: RequestInfo) -> Any:
        request_params = self.dump_request_params(request_info)
        response_model = request_params.pop("response_model")

        request_params = self.before_request(request_params)

        response = requests.request(**request_params, timeout=self.timeout)
        response.raise_for_status()

        data = response.json()
        if response_model is not None:
            return response_model.model_validate(data, from_attributes=True)
        return data
