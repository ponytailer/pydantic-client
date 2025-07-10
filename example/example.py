from typing import Optional
from pydantic import BaseModel
from pydantic_client import RequestsWebClient, AiohttpWebClient, HttpxWebClient, get

class User(BaseModel):
    id: str
    name: str
    email: Optional[str] = None

# 同步客户端
class MySyncClient(RequestsWebClient):
    @get("/users/{user_id}")
    def get_user_by_id(self, user_id: str) -> User:
        ...

# AIOHTTP异步客户端
class MyAiohttpClient(AiohttpWebClient):
    @get("/users/{user_id}")
    async def get_user_by_id(self, user_id: str) -> User:
        ...

# HTTPX异步客户端
class MyHttpxClient(HttpxWebClient):
    @get("/users/{user_id}")
    async def get_user_by_id(self, user_id: str) -> User:
        ...

# 使用示例
def sync_example():
    config = {
        "base_url": "https://api.example.com",
        "headers": {"Authorization": "Bearer token"}
    }
    
    client = MySyncClient.from_config(config)
    user = client.get_user_by_id("123")
    print(f"Got user: {user}")

async def async_example():
    config = {
        "base_url": "https://api.example.com",
        "headers": {"Authorization": "Bearer token"}
    }
    
    # 使用 aiohttp
    aiohttp_client = MyAiohttpClient.from_config(config)
    user1 = await aiohttp_client.get_user_by_id("123")
    print(f"Got user from aiohttp: {user1}")
    
    # 使用 httpx
    httpx_client = MyHttpxClient.from_config(config)
    user2 = await httpx_client.get_user_by_id("123")
    print(f"Got user from httpx: {user2}")
