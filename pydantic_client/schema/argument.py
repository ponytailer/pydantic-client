from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class RequestParameters(BaseModel):
    """参数处理结果"""
    params: Dict[str, Any]
    headers: Optional[Dict[str, str]] = None


class PathInfo(BaseModel):
    """路径处理结果"""
    formatted_path: str
    remaining_params: Dict[str, Any]


class RequestData(BaseModel):
    """请求数据"""
    query_params: Optional[Dict[str, Any]] = None
    json_data: Optional[Dict[str, Any]] = None
    form_data: Optional[Dict[str, Any]] = None


class ResponseTypeInfo(BaseModel):
    """响应类型信息"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    response_model: Optional[type] = None
    is_file_response: bool = False
    return_type: type
