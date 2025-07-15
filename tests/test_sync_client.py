import pytest
import requests_mock
import requests
from pydantic import BaseModel
from pydantic_client import RequestsWebClient, get, post


class User(BaseModel):
    id: str
    name: str
    email: str


class TestClient(RequestsWebClient):
    @get("/users/{user_id}")
    def get_user(self, user_id: str) -> User:
        ...

    @post("/users")
    def create_user(self, name: str, email: str) -> User:
        ...

    @get("/users/string")
    def get_user_string(self, name: str) -> str:
        ...
    
    @get("/users/bytes")
    def get_user_bytes(self, name: str) -> bytes:
        ...
    
    @get("/users/dict")
    def get_user_dict(self, name: str) -> dict:
        ...


def test_sync_get_request():
    with requests_mock.Mocker() as m:
        m.get(
            'http://example.com/users/123',
            json={"id": "123", "name": "Test User", "email": "test@example.com"}
        )

        client = TestClient(base_url="http://example.com")
        response = client.get_user("123")

        assert isinstance(response, User)
        assert response.id == "123"
        assert response.name == "Test User"
        assert response.email == "test@example.com"


def test_sync_post_request():
    with requests_mock.Mocker() as m:
        m.post(
            'http://example.com/users',
            json={"id": "123", "name": "New User", "email": "new@example.com"}
        )

        client = TestClient(base_url="http://example.com")
        response = client.create_user(
            name="New User",
            email="new@example.com"
        )

        assert isinstance(response, User)
        assert response.id == "123"
        assert response.name == "New User"
        assert response.email == "new@example.com"


def test_sync_error_handling():
    with requests_mock.Mocker() as m:
        m.get(
            'http://example.com/users/123',
            status_code=404,
            json={"error": "User not found"}
        )

        client = TestClient(base_url="http://example.com")
        with pytest.raises(requests.exceptions.HTTPError):
            client.get_user("123")


def test_sync_get_string_request():
    with requests_mock.Mocker() as m:
        m.get(
            'http://example.com/users/string',
            text="ac"
        )

        client = TestClient(base_url="http://example.com")
        response = client.get_user_string("123")

        assert isinstance(response, str)
        assert response == "ac"


def test_sync_get_bytes_request():
    with requests_mock.Mocker() as m:
        m.get(
            'http://example.com/users/bytes',
            content="123".encode()
        )

        client = TestClient(base_url="http://example.com")
        response = client.get_user_bytes("123")

        assert isinstance(response, bytes)
        assert response == b"123"


def test_sync_get_dict_request():
    with requests_mock.Mocker() as m:
        m.get(
            'http://example.com/users/dict',
            json={"user": 123}
        )

        client = TestClient(base_url="http://example.com")
        response = client.get_user_dict("123")

        assert isinstance(response, dict)
        assert response == {"user": 123}
