import inspect
import logging
import time
import statsd

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TypeVar, List

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

        if statsd_address:
            host, port = statsd_address.split(':')
            self._statsd_client = statsd.StatsClient(host, int(port))


    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'BaseWebClient':
        return cls(
            base_url=config['base_url'],
            headers=config.get('headers'),
            timeout=config.get('timeout', 30),
            session=config.get('session', None),
            statsd_address=config.get('statsd_address')
        )
    
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
        return request_params

    @abstractmethod
    def _request(self, request_info: RequestInfo) -> Any:
        ...
    

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
