from typing import Dict, Optional, Any, Type

from pydantic import BaseModel


class RequestInfo(BaseModel):
    method: str
    path: str
    params: Optional[Dict[str, Any]] = {}
    json: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, Any]] = {}
    response_model: Optional[Type[BaseModel]] = None
