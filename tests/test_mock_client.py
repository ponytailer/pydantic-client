import pytest
from typing import List, Optional
from pydantic import BaseModel

from pydantic_client.sync_client import RequestsWebClient
from pydantic_client.async_client import AiohttpWebClient, HttpxWebClient
from pydantic_client.decorators import get, post


# 定义测试用的响应模型
class User(BaseModel):
    name: str
    age: int
    email: Optional[str] = None


class UserList(BaseModel):
    users: List[User]
    total: int


# 定义测试客户端
class TestClient(RequestsWebClient):
    @get("/users")
    def get_users(self) -> UserList:
        """Get users list"""
        pass
    
    @get("/users/{user_id}")
    def get_user(self, user_id: int) -> User:
        """Get a single user"""
        pass
    
    @post("/users")
    def create_user(self, user: User) -> User:
        """Create a user"""
        pass


class AsyncTestClient(AiohttpWebClient):
    @get("/users")
    async def get_users(self) -> UserList:
        """Get users list"""
        pass


class HttpxTestClient(HttpxWebClient):
    @get("/users")
    async def get_users(self) -> UserList:
        """Get users list"""
        pass


def test_sync_client_mock():
    """测试同步客户端的mock功能"""
    client = TestClient(base_url="https://example.com")
    
    mock_data = [
        {
            "name": "get_users",
            "output": {
                "users": [
                    {"name": "test1", "age": 30, "email": "test1@example.com"},
                    {"name": "test2", "age": 25, "email": "test2@example.com"}
                ],
                "total": 2
            }
        },
        {
            "name": "get_user",
            "output": {
                "name": "test1",
                "age": 30,
                "email": "test1@example.com"
            }
        }
    ]
    
    client.set_mock_config(mock_config=mock_data)
    
    # 验证mock响应
    users = client.get_users()
    assert isinstance(users, UserList)
    assert len(users.users) == 2
    assert users.users[0].name == "test1"
    assert users.users[1].name == "test2"
    assert users.total == 2
    
    user = client.get_user(1)
    assert isinstance(user, User)
    assert user.name == "test1"
    assert user.age == 30
    assert user.email == "test1@example.com"


def test_from_config_with_mock():
    """测试从配置创建客户端时设置mock"""
    config = {
        "base_url": "https://example.com",
        "timeout": 10,
        "mock_config": [
            {
                "name": "get_users",
                "output": {
                    "users": [
                        {"name": "config_test", "age": 40, "email": "config@example.com"}
                    ],
                    "total": 1
                }
            }
        ]
    }
    
    client = TestClient.from_config(config)
    
    # 验证mock响应
    users = client.get_users()
    assert isinstance(users, UserList)
    assert len(users.users) == 1
    assert users.users[0].name == "config_test"
    assert users.total == 1


def test_invalid_mock_config():
    """测试无效的mock配置"""
    client = TestClient(base_url="https://example.com")
    
    # 测试非列表类型
    with pytest.raises(ValueError, match="Mock config must be a list"):
        client.set_mock_config(mock_config={"not": "a list"})
    
    # 测试缺少必要字段的配置
    client.set_mock_config(mock_config=[
        {"name": "get_users"},  # 没有output
        {"output": "some data"}  # 没有name
    ])
    # 验证没有mock被设置
    assert client._mock_config == {}


@pytest.mark.asyncio
async def test_async_client_mock():
    """测试异步客户端的mock功能"""
    client = AsyncTestClient(base_url="https://example.com")
    
    client.set_mock_config(mock_config=[
        {
            "name": "get_users",
            "output": {
                "users": [
                    {"name": "async_test", "age": 35, "email": "async@example.com"}
                ],
                "total": 1
            }
        }
    ])
    
    # 验证异步mock响应
    users = await client.get_users()
    assert isinstance(users, UserList)
    assert len(users.users) == 1
    assert users.users[0].name == "async_test"
    assert users.total == 1


@pytest.mark.asyncio
async def test_httpx_client_mock():
    """测试基于httpx的异步客户端的mock功能"""
    client = HttpxTestClient(base_url="https://example.com")
    
    client.set_mock_config(mock_config=[
        {
            "name": "get_users",
            "output": {
                "users": [
                    {"name": "httpx_test", "age": 45, "email": "httpx@example.com"}
                ],
                "total": 1
            }
        }
    ])
    
    # 验证httpx客户端的mock响应
    users = await client.get_users()
    assert isinstance(users, UserList)
    assert len(users.users) == 1
    assert users.users[0].name == "httpx_test"
    assert users.total == 1
