import requests_mock
from enum import Enum
from typing import Union, Optional, overload, Literal
from pydantic import BaseModel
from pydantic_client import RequestsWebClient, get


class ModelA(BaseModel):
    test_A: str

class ModelB(BaseModel):
    test_B: str

class UnionClient(RequestsWebClient):
    @overload
    def get_type_response(self, type: Literal["A"]) -> ModelA: ...
    
    @overload
    def get_type_response(self, type: Literal["B"]) -> ModelB: ...
    
    @get("/types?type={type}")
    def get_type_response(self, type: str) -> Union[ModelA, ModelB]:
        ...

def test_union_type_handler():
    with requests_mock.Mocker() as m:
        m.get('http://example.com/types?type=A', json={"test_A": "name_A"})
        m.get('http://example.com/types?type=B', json={"test_B": "name_B"})

        client = UnionClient(base_url="http://example.com")
        
        result_a = client.get_type_response('A')
        assert isinstance(result_a, ModelA)
        assert result_a.test_A == "name_A"
        
        result_b = client.get_type_response('B')
        assert isinstance(result_b, ModelB)
        assert result_b.test_B == "name_B"