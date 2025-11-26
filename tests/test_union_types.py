import requests_mock
from typing import Union
from pydantic import BaseModel
from pydantic_client import RequestsWebClient, get


class ModelA(BaseModel):
    type: str
    data: str


class ModelB(BaseModel):
    type: str
    value: int


class TestUnionClient(RequestsWebClient):
    @get("/test")
    def get_union_response(self) -> Union[ModelA, ModelB]:
        ...


def test_union_type_first_model():
    with requests_mock.Mocker() as m:
        m.get(
            'http://example.com/test',
            json={"type": "A", "data": "test"}
        )

        client = TestUnionClient(base_url="http://example.com")
        result = client.get_union_response()

        assert isinstance(result, ModelA)
        assert result.type == "A"
        assert result.data == "test"


def test_union_type_second_model():
    with requests_mock.Mocker() as m:
        m.get(
            'http://example.com/test',
            json={"type": "B", "value": 42}
        )

        client = TestUnionClient(base_url="http://example.com")
        result = client.get_union_response()

        assert isinstance(result, ModelB)
        assert result.type == "B"
        assert result.value == 42


def test_union_type_fallback_to_first_valid():
    with requests_mock.Mocker() as m:
        m.get(
            'http://example.com/test',
            json={"type": "C", "data": "fallback", "value": 123}
        )

        client = TestUnionClient(base_url="http://example.com")
        result = client.get_union_response()

        # Should successfully parse as ModelA since it has required fields
        assert isinstance(result, ModelA)
        assert result.type == "C"
        assert result.data == "fallback"