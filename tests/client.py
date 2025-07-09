from typing import Optional
from pydantic import BaseModel


class FunctionAnalysisRequest(BaseModel):
    project_name: Optional[str]
    struct_code: Optional[str]
    struct_level_code: Optional[str]
    struct_name: str
    function_type: Optional[str]
    


class HTTPValidationError(BaseModel):
    detail: Optional[list[str]]
    


class LoseEffectRequest(BaseModel):
    struct_name: str
    function_description: str
    


class LoseEffectResponse(BaseModel):
    failure_type_code: str
    failure_description: str
    


class ValidationError(BaseModel):
    loc: list[str]
    msg: str
    type: str
    


class WebClient:
    
    @get("/fmea-agent/v1/hello")
    def get_fmea_agent_v1_hello(self):
        ...
    
    @post("/fmea-agent/v1/function_analysis")
    def post_fmea_agent_v1_function_analysis(self, function_analysis_request: FunctionAnalysisRequest):
        ...
    
    @post("/fmea-agent/v1/lose_effect_analysis/{lose_id}")
    def post_fmea_agent_v1_lose_effect_analysis(self, lose_id: int, name: Optional[str], lose_effect_request: LoseEffectRequest):
        ...
    