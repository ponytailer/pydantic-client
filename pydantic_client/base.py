import inspect
import json
import logging
import re
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TypeVar, List, get_origin, get_args

import pydantic
import statsd
from pydantic import BaseModel

from .schema import RequestInfo

T = TypeVar('T', bound=BaseModel)
logger = logging.getLogger(__name__)


class SpanContext:
    def __init__(self, client, prefix: Optional[str] = None):
        self.client = client
        self.prefix = prefix or "api"
        self.start_time = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        logger.info(f"[{self.prefix}] span start")
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = 1000 * (time.perf_counter() - self.start_time)
        logger.info(f"[{self.prefix}] span end, elapsed: {elapsed}ms")
        if self.client._statsd_client:
            self.client._statsd_client.timing(f"{self.prefix}.elapsed", int(elapsed))

class PydanticClientValidationError(ValueError): ...

class BaseWebClient(ABC):
    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        session: Any = None,
        statsd_address: str = None
    ):
        self.base_url = base_url.rstrip('/')
        self.headers = headers or {}
        self.timeout = timeout
        self.session = session
        self._statsd_client = None
        self._mock_config: Dict[str, Any] = {}

        if statsd_address:
            host, port = statsd_address.split(':')
            self._statsd_client = statsd.StatsClient(host, int(port))


    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'BaseWebClient':
        client = cls(
            base_url=config['base_url'],
            headers=config.get('headers'),
            timeout=config.get('timeout', 30),
            session=config.get('session', None),
            statsd_address=config.get('statsd_address')
        )
        
        # Set mock config if provided
        if 'mock_config' in config:
            client.set_mock_config(mock_config=config['mock_config'])
            
        return client
    
    def before_request(self, request_params: Dict[str, Any]) -> Dict[str, Any]:
        """before request, you can do something by yourself
        such as: cal signature, etc."""
        return request_params

    def _make_url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def span(self, prefix: Optional[str] = None):
        return SpanContext(self, prefix)
    
    def dump_request_params(self, request_info: RequestInfo) -> Dict[str, Any]:
        request_params = request_info.model_dump(by_alias=True)
        url = self._make_url(request_params.pop("path"))
        # Merge headers
        request_headers = self.headers.copy()
        if request_info.headers:
            request_headers.update(request_info.headers)
        
        request_params["headers"] = request_headers
        request_params["url"] = url
        request_params.pop("function_name", None)
        # response_extract_path 会在 _request 方法中处理，所以保留
        return request_params

    def set_mock_config(
        self,
        *,
        mock_config_path: Optional[str] = None,
        mock_config: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Set mock configuration for API responses.
        
        Example:
        ```python
        client.set_mock_config(mock_config=[
            {
                "name": "get_users",
                "output": {
                    "users": [
                        {"name": "john", "age": 1}
                    ]
                }
            }
        ])
        ```
        
        or from file:
        ```python
        client.set_mock_config(mock_config_path="path/to/mock_config.json")
        ```
        
        Args:
            mock_config_path: Path to JSON file containing mock configurations
            mock_config: List of dicts with 'name' and 'output' keys
        """
        
        if mock_config_path:
            with open(mock_config_path, 'r') as f:
                mock_config_data = json.load(f)
        else:
            mock_config_data = mock_config

        if not isinstance(mock_config_data, list):
            raise ValueError("Mock config must be a list")
            
        self._mock_config = {
            item["name"]: item["output"]
            for item in mock_config_data if "name" in item and "output" in item
        }
        if self._mock_config:
            logger.warning("Mock configuration enabled - API calls will return mock data")
    
    def _get_mock_response(self, request_info: RequestInfo) -> Optional[Any]:
        """Get mock response for a method if available in mock config"""
        if not self._mock_config:
            return None

        name = request_info.function_name
        
        if name not in self._mock_config:
            logger.warning(f"No mock found for method: {name}")
            return None

        mosk_data = self._mock_config[name]

        mosk_data_bytes: bytes | None = None

        if isinstance(mosk_data, list) or isinstance(mosk_data, dict):
            mosk_data_bytes = json.dumps(mosk_data).encode()

        if isinstance(mosk_data, pydantic.BaseModel):
            mosk_data_bytes = mosk_data.model_dump_json().encode()

        if isinstance(mosk_data, str):
            mosk_data_bytes = mosk_data.encode()

        if isinstance(mosk_data, bytes):
            mosk_data_bytes = mosk_data

        if mosk_data is not None:
            assert mosk_data_bytes is not None, f'Unknown mosk output type: {type(mosk_data)}'
        return self._cast_response_to_response_model(mosk_data_bytes, request_info)
        
    @abstractmethod
    def _request(self, request_info: RequestInfo) -> Any:
        ...

    def _cast_response_to_response_model(self, response: bytes, request_info: RequestInfo):
        response_model = request_info.response_model
        if response_model is None or response is None: return response

        if response_model is bytes:
            return response

        response_str = response.decode()

        if response_model is str:
            return response_str

        if request_info.response_extract_path:
            response_json: dict | list | None = self._extract_nested_data(
                json.loads(response_str),
                request_info.response_extract_path
            )

            # extraction fail
            if response_json is None:
                return None
        else:
            # allow using model_validate_json instead of json.loads() for speed up pydantic models
            response_json: dict | list | None = None

        # handle generic types dict[...], list[...]
        # using get_origin for get real response_model class
        response_model_origin = response_model
        if not inspect.isclass(response_model):
            response_model_origin = response_model
            response_model = get_origin(response_model)

        # handle type hint: TestModel
        if issubclass(response_model, pydantic.BaseModel):
            if response_json is None:
                return response_model.model_validate_json(response_str, by_alias=True)
            else:
                return response_model.model_validate(response_json, by_alias=True)

        if response_json is None:
            response_json: dict | list = json.loads(response_str)

        if issubclass(response_model, dict):
            return response_json

        # handle type hint: list[...] or just list
        if issubclass(response_model, list) or get_origin(response_model) is list:
            # handle type hint: list[...]
            nested_types = get_args(response_model_origin)
            if len(nested_types) > 0:
                nested_type = nested_types[0]

                # if hint is: list[dict[...]] - unsupported
                if not inspect.isclass(nested_type) or len(get_args(nested_type)) > 0:
                    raise PydanticClientValidationError(f"Incorrect type hint on return value on API {request_info.path}, simplify")

                # handle list[TestModel]
                if issubclass(nested_type, pydantic.BaseModel):
                    return [nested_type.model_validate(item, by_alias=True) for item in response_json]

            return response_json

        logger.warning(f"Unknown response_model {response_model} on API {request_info.path} or "
                       f"incorrect response type {type(response_json)}, returned {type(response_json)}")
        return response_json
        
    def _extract_nested_data(self, data: Dict[str, Any], path: str) -> Any:
        """
        Extract and parse data from nested response data
        
        Args:
            data: JSON response data
            path: JSON path expression, e.g. "$.data.user" or "$.data.items[0]"
            model_type: Pydantic model type for parsing the extracted data
        """
        # Preprocess path, remove $ prefix
        if path.startswith('$'):
            path = path[2:].lstrip('.')
            
        # Extract all components from the path
        path_components = re.split(r'\.|\[|\]', path)
        path_components = [p for p in path_components if p]
        
        current = data
        for component in path_components:
            if component.isdigit():
                idx = int(component)
                if isinstance(current, list) and 0 <= idx < len(current):
                    current = current[idx]
                else:
                    return None
            elif isinstance(current, dict):
                current = current.get(component)
                if current is None:
                    return None
            else:
                return None

        return current

    def register_agno_tools(self, agent):
        """
        Register all agno tools of this client instance to the given agent.
        Compatible with agno agent's set_tools/add_tool API.
        """
        tools = []
        for tool_info in self.get_agno_tools():
            tool_name = tool_info['name']
            tool = dict(
                name=tool_name,
                description=tool_info.get('description', ''),
                parameters=tool_info.get('parameters', {}),
                call=lambda params, tool_name=tool_name: getattr(self, tool_name)(**params)
            )
            tools.append(tool)
        agent.set_tools(tools)

    @classmethod
    def get_agno_tools(cls) -> List[Dict[str, Any]]:
        """Get all registered Agno tools from the client"""
        tools = []
        for name, method in inspect.getmembers(cls, inspect.isfunction):
            if hasattr(method, '_agno_tool'):
                tools.append(method._agno_tool)
        return tools
