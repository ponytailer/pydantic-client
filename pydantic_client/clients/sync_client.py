from typing import Any, Dict, Optional, TypeVar
import logging

import requests
from pydantic import BaseModel

from .base import BaseWebClient, RequestInfo

logger = logging.getLogger(__name__)

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
        # Check if there's a mock response for this method
        mock_response = self._get_mock_response(request_info)
        if mock_response is not None:
            return mock_response

        request_params = self.dump_request_params(request_info)
        response_model = request_params.pop("response_model")
        extract_path = request_params.pop("response_extract_path", None)

        request_params = self.before_request(request_params)

        response = requests.request(**request_params, timeout=self.timeout)
        response.raise_for_status()
        
        if response_model is str:
            return response.text
        elif response_model is bytes:
            return response.content
        elif extract_path:
            # Process nested path extraction
            return self._extract_nested_data(response.json(), extract_path, response_model)
        elif not response_model or response_model is dict or getattr(response_model, '__module__', None) == 'inspect':
            return response.json()
        elif hasattr(response_model, 'model_validate'):
            return response_model.model_validate(response.json(), from_attributes=True)
        else:
            return response.json()
        

