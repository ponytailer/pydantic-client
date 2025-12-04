from typing import Dict, Optional, Any
from pydantic import BaseModel, Field


class RequestInfo(BaseModel):
    method: str
    path: str
    params: Optional[Dict[str, Any]] = {}
    json_data: Optional[Dict[str, Any]] = Field(default=None, alias='json')
    data: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, Any]] = {}
    response_model: Optional[Any] = None
    function_name: Optional[str] = None
    response_extract_path: Optional[str] = None
