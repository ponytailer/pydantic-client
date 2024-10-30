from typing import Any, Callable, Dict, Optional, Type, Union

from pydantic import BaseModel

from pydantic_client.schema.file import File


class MethodInfo(BaseModel):
    func: Callable
    http_method: str
    url: str
    request_type: Dict[str, Any]
    response_type: Optional[Type]
    form_body: bool
