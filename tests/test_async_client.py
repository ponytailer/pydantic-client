import pytest
from pydantic import BaseModel
from pydantic_client import AiohttpWebClient, HttpxWebClient, get, post


class User(BaseModel):
    id: str
    name: str
    email: str


class TestAiohttpClient(AiohttpWebClient):
    @get("/users/{user_id}")
    async def get_user(self, user_id: str) -> User:
        ...

    @post("/users")
    async def create_user(self, name: str, email: str) -> User:
        ...


class TestHttpxClient(HttpxWebClient):
    @get("/users/{user_id}")
    async def get_user(self, user_id: str) -> User:
        ...

    @post("/users")
    async def create_user(self, name: str, email: str) -> User:
        ...


@pytest.mark.asyncio
async def test_aiohttp_get_request(mock_server, base_url):
    client = TestAiohttpClient(base_url=base_url)
    response = await client.get_user("123")

    assert isinstance(response, User)
    assert response.id == "123"
    assert response.name == "User 123"
    assert response.email == "user123@example.com"


@pytest.mark.asyncio
async def test_httpx_get_request(mock_server, base_url):
    client = TestHttpxClient(base_url=base_url)
    response = await client.get_user("123")

    assert isinstance(response, User)
    assert response.id == "123"
    assert response.name == "User 123"
    assert response.email == "user123@example.com"


@pytest.mark.asyncio
async def test_aiohttp_error_handling(mock_server, base_url):
    client = TestAiohttpClient(base_url=f"{base_url}/nonexistent")
    with pytest.raises(BaseException):
        await client.get_user("123")


@pytest.mark.asyncio
async def test_httpx_error_handling(mock_server, base_url):
    client = TestHttpxClient(base_url=f"{base_url}/nonexistent")
    with pytest.raises(BaseException):
        await client.get_user("123")