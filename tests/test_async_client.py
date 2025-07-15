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
    
    @post("/users/string")
    async def get_user_string(self, name: str) -> str:
        ...
    
    @post("/users/bytes")
    async def get_user_bytes(self, name: str) -> bytes:
        ...
    
    @post("/users/dict")
    async def get_user_dict(self, name: str) -> dict:
        ...


class TestHttpxClient(HttpxWebClient):
    @get("/users/{user_id}")
    async def get_user(self, user_id: str) -> User:
        ...

    @post("/users")
    async def create_user(self, name: str, email: str) -> User:
        ...
    
    @post("/users/string")
    async def get_user_string(self, name: str) -> str:
        ...
    
    @post("/users/bytes")
    async def get_user_bytes(self, name: str) -> bytes:
        ...
    
    @post("/users/dict")
    async def get_user_dict(self, name: str) -> dict:
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


@pytest.mark.asyncio
async def test_aiohttp_get_string_request(mock_server, base_url):
    client = TestAiohttpClient(base_url=base_url)
    response = await client.get_user_string("123")

    assert isinstance(response, str)
    assert response == "abc"


@pytest.mark.asyncio
async def test_aiohttp_get_bytes_request(mock_server, base_url):
    client = TestAiohttpClient(base_url=base_url)
    response = await client.get_user_bytes("123")
    print(response)
    assert isinstance(response, bytes)
    assert response == "abc".encode()


@pytest.mark.asyncio
async def test_httpx_get_dict_request(mock_server, base_url):
    client = TestAiohttpClient(base_url=base_url)
    response = await client.get_user_dict("123")

    assert isinstance(response, dict)
    assert response == {"users": []}


@pytest.mark.asyncio
async def test_httpx_get_string_request(mock_server, base_url):
    client = TestHttpxClient(base_url=base_url)
    response = await client.get_user_string("123")

    assert isinstance(response, str)
    assert response == "abc"


@pytest.mark.asyncio
async def test_httpx_get_bytes_request(mock_server, base_url):
    client = TestHttpxClient(base_url=base_url)
    response = await client.get_user_bytes("123")
    print(response)
    assert isinstance(response, bytes)
    assert response == "abc".encode()


@pytest.mark.asyncio
async def test_aiohttp_get_dict_request(mock_server, base_url):
    client = TestHttpxClient(base_url=base_url)
    response = await client.get_user_dict("123")

    assert isinstance(response, dict)
    assert response == {"users": []}
