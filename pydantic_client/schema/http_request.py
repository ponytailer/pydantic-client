from typing import Dict, Optional

from pydantic import BaseModel


class HttpRequest(BaseModel):
    data: Optional[Dict] = {}
    json: Optional[Dict] = {}
    url: str
    method: str
