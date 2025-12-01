from json import JSONDecodeError
from typing import Optional, Any

from pydantic import BaseModel, ValidationError

from pydantic_client import RequestsWebClient, get
from pydantic_client.base import PydanticClientValidationError


class User(BaseModel):
    name: str
    age: int
    email: Optional[str] = None

class TestClient(RequestsWebClient):
    @get("/just_string")
    def just_string(self) -> str:
        ...

    @get("/just_string_neg")
    def just_string_neg(self) -> str:
        ...

    @get("/too_complex_return_type")
    def too_complex_return_type(self) -> list[dict[str, Any]]:
        ...

    @get("/just_bytes")
    def just_bytes(self) -> bytes:
        ...

    @get("/list_of_some")
    def list_of_some(self) -> list:
        ...

    @get("/list_of_some_neg")
    def list_of_some_neg(self) -> list:
        ...

    @get("/get_users_decorator_list")
    def get_users_decorator_list(self) -> list[User]:
        ...

    @get("/get_users_decorator_list_neg")
    def get_users_decorator_list_neg(self) -> list[User]:
        ...

    @get("/get_users_decorator_list_nested", response_extract_path='$.users')
    def get_users_decorator_list_nested(self) -> list[User]:
        ...


def test_return_primitive_types():
    client = TestClient(base_url="https://example.com")
    mock_data = [
        {
            "name": "just_string",
            "output": "some-string"
        },
        {
            "name": "just_string_neg",
            "output": ['trash', 'data']
        },
        {
            "name": "list_of_some_neg",
            "output": b'some-bytes-not-list'
        },
        {
            "name": "just_bytes",
            "output": b'some-bytes'
        },
        {
            "name": "list_of_some",
            "output": ['a', 0, 1]
        },
    ]

    client.set_mock_config(mock_config=mock_data)

    data = client.just_string()
    assert isinstance(data, str)
    assert data == 'some-string'

    data = client.just_bytes()
    assert isinstance(data, bytes)
    assert data == b'some-bytes'

    data = client.list_of_some()
    assert isinstance(data, list)
    assert len(data) == 3
    assert data[0] == 'a'
    assert data[2] == 1

    data = client.just_string_neg()
    assert isinstance(data, str)
    assert data == '["trash", "data"]'

    try:
        client.list_of_some_neg()
        assert False, 'must be json decoding error'
    except JSONDecodeError:
        pass


def test_generic_types():
    client = TestClient(base_url="https://example.com")

    mock_data = [
        {
            "name": "get_users_decorator_list",
            "output": [
                {"name": "test1", "age": 30, "email": "test1@example.com"},
                {"name": "test2", "age": 25, "email": "test2@example.com"}
            ]
        },
        {
            "name": "get_users_decorator_list_nested",
            "output": {
                "users": [
                    {"name": "test3", "age": 30, "email": "test1@example.com"},
                    {"name": "test4", "age": 25, "email": "test2@example.com"}
                ],
                "total": 2
            }
        },
        {
            "name": 'get_users_decorator_list_neg',
            "output": {
                "users": {'trash': 'object'},
                "total": 2
            }
        }
    ]

    client.set_mock_config(mock_config=mock_data)

    users = client.get_users_decorator_list()
    assert isinstance(users, list)
    assert len(users) == 2
    assert isinstance(users[1], User)
    assert users[1].name == 'test2'

    users = client.get_users_decorator_list_nested()
    assert isinstance(users, list)
    assert len(users) == 2
    assert isinstance(users[1], User)
    assert users[1].name == 'test4'

    try:
        client.get_users_decorator_list_neg()
        assert False, 'must be pydantic model validation error'
    except ValidationError:
        pass

def test_incorrect_return_type():
    client = TestClient(base_url="https://example.com")

    mock_data = [
        {
            "name": "too_complex_return_type",
            "output": [
                {"name": "test1", "age": 30, "email": "test1@example.com"},
                {"name": "test2", "age": 25, "email": "test2@example.com"}
            ]
        },
    ]

    client.set_mock_config(mock_config=mock_data)

    try:
        client.too_complex_return_type()
        assert False, 'must be raises exception PydanticClientValidationError'
    except PydanticClientValidationError as e:
        pass

