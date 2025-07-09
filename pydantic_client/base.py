from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type, TypeVar

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
        pass
