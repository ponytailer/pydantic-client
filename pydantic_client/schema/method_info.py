from typing import Any, Callable, Dict, Optional

from pydantic import BaseModel


class MethodInfo(BaseModel):
    func: Callable
    http_method: str
    url: str
    request_type: Dict[str, Any]
    response_type: Optional[Any]
    form_body: bool
