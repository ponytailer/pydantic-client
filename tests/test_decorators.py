import pytest
import requests_mock
from typing import Optional
from pydantic import BaseModel
from pydantic_client import get, post, RequestsWebClient, AiohttpWebClient


class User(BaseModel):
    id: str
    name: str
    email: Optional[str] = None


class TestSyncClient(RequestsWebClient):
    @get("/users?page={page}&per_page={per_page}&name=kk")
    def list_users(self, page: int = 1, per_page: int = 10):
        ...

    @get("/users/{user_id}")
    def get_user(self, user_id: str) -> User:
        ...

    @post("/users")
    def create_user(self, name: str, email: Optional[str] = None) -> User:
        ...


class TestAsyncClient(AiohttpWebClient):
    @get("/users?page={page}&per_page={per_page}&name=kk")
    async def list_users(self, page: int = 1, per_page: int = 10):
        ...

    @get("/users/{user_id}")
    async def get_user(self, user_id: str) -> User:
        ...

    @post("/users")
    async def create_user(self, name: str, email: Optional[str] = None) -> User:
        ...


def test_path_params():
    with requests_mock.Mocker() as m:
        m.get(
            'http://example.com/users/123',
            json={"id": "123", "name": "Test User", "email": "test@example.com"}
        )

        client = TestSyncClient(base_url="http://example.com")
        response = client.get_user("123")

        assert isinstance(response, User)
        assert response.id == "123"


def test_query_params():
    with requests_mock.Mocker() as m:
        m.get(
            'http://example.com/users?page=2&per_page=20',
            json={"users": []}
        )

        client = TestSyncClient(base_url="http://example.com")
        client.list_users(page=2, per_page=20)

        assert m.called
        assert m.last_request.qs == {'page': ['2'], 'per_page': ['20']}


@pytest.mark.asyncio
async def test_async_path_params(mock_server, base_url):
    client = TestAsyncClient(base_url=base_url)
    response = await client.get_user("123")
   
    assert isinstance(response, User)
    assert response.id == "123"


@pytest.mark.asyncio
async def test_async_query_params(mock_server, base_url):
    client = TestAsyncClient(base_url=base_url)
    await client.list_users(page=2, per_page=20)
