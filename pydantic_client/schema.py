from typing import Dict, Optional, Any
from pydantic import BaseModel


class RequestInfo(BaseModel):
    method: str
    path: str
    params: Optional[Dict[str, Any]] = {}
    json: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, Any]] = {}
    response_model: Optional[Any] = None
    function_name: Optional[str] = None
    response_extract_path: Optional[str] = None
