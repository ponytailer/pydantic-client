from typing import Any, Callable, Dict, Type

from pydantic import BaseModel

from pydantic_client.clients.abstract_client import AbstractClient


class MethodInfo(BaseModel):
    func: Callable
    http_method: str
    url: str
    request_type: Dict[str, Any]
    response_type: Type
    form_body: bool

    def __get__(self, instance: AbstractClient, objtype=None):
        return instance.runner_class(instance, method_info=self)
