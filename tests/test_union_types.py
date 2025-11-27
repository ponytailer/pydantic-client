import requests_mock
from enum import Enum
from typing import Union, Optional, overload, Literal
from pydantic import BaseModel
from pydantic_client import RequestsWebClient, get


class ModelA(BaseModel):
    name: str
    book: Optional[str] = None


class ModelB(BaseModel):
    name: str
    other_book: Optional[str] = None


class TestUnionClient(RequestsWebClient):
    @overload
    def get_type_response(self, type: Literal["A"]) -> ModelA: ...
    
    @overload
    def get_type_response(self, type: Literal["B"]) -> ModelB: ...
    
    @get("/types?type={type}")
    def get_type_response(self, type: str) -> Union[ModelA, ModelB]:
        ...

def test_union_type_handler():
    with requests_mock.Mocker() as m:
        m.get('http://example.com/types?type=A', json={"name": "test_A" })
        m.get('http://example.com/types?type=B', json={"name": "test_B" })

        client = TestUnionClient(base_url="http://example.com")
        
        result_a = client.get_type_response('A')
        assert isinstance(result_a, ModelA)
        assert result_a.name == "test_A"
        
        result_b = client.get_type_response('B')
        assert isinstance(result_b, ModelB)
        assert result_b.name == "test_B"