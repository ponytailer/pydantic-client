import inspect
import json
import logging
import time
import statsd
import re

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TypeVar, List, Type, get_origin, get_args

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
        request_params = request_info.model_dump()
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
            
        mock_response = self._mock_config[name]
        response_model = request_info.response_model


        extract_path = request_info.response_extract_path

        if extract_path:
            return self._extract_nested_data(mock_response, extract_path, response_model)
        elif response_model and not isinstance(response_model, type) or response_model in (str, bytes):
            return mock_response
        elif response_model:
            return response_model.model_validate(mock_response, from_attributes=True)
        return mock_response
        
    @abstractmethod
    def _request(self, request_info: RequestInfo) -> Any:
        ...
        
    def _extract_nested_data(self, data: Dict[str, Any], path: str, model_type: Type) -> Any:
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
        
        if current is not None:
            # Handle list types
            origin = get_origin(model_type)
            
            if origin is list or origin is List:
                item_type = get_args(model_type)[0]
                if isinstance(current, list):
                    return [item_type.model_validate(item) for item in current]
            elif hasattr(model_type, 'model_validate'):
                return model_type.model_validate(current)
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
