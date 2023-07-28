from typing import Dict, Optional

from pydantic import BaseModel


class HttpRequest(BaseModel):
    data: Optional[Dict] = {}
    json_body: Optional[Dict] = {}
    url: str
    method: str
