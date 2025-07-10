import inspect

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type, TypeVar, List

from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


class BaseWebClient(ABC):
    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30
    ):
        self.base_url = base_url.rstrip('/')
        self.headers = headers or {}
        self.timeout = timeout

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'BaseWebClient':
        return cls(
            base_url=config['base_url'],
            headers=config.get('headers'),
            timeout=config.get('timeout', 30)
        )

    def _make_url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    @abstractmethod
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
        ...
    

    def register_agno_tools(self, agent):
        """
        Register all agno tools of this client instance to the given agent.
        Each tool will be registered with its description, parameters, and a call bound to this instance.

        :param agent: The agent instance which supports .register_tool(name, description, parameters, call)
        """
        for tool_info in self.get_agno_tools():
            tool_name = tool_info['name']
            agent.register_tool(
                name=tool_name,
                description=tool_info.get('description', ''),
                parameters=tool_info.get('parameters', {}),
                call=lambda params, tool_name=tool_name: getattr(self, tool_name)(**params)
            )

    @classmethod
    def get_agno_tools(cls) -> List[Dict[str, Any]]:
        """Get all registered Agno tools from the client"""
        tools = []
        for name, method in inspect.getmembers(cls, inspect.isfunction):
            if hasattr(method, '_agno_tool'):
                tools.append(method._agno_tool)
        return tools
