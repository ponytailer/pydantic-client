import requests_mock
import logging
from typing import List, Optional
from pydantic import BaseModel

from pydantic_client.sync_client import RequestsWebClient
from pydantic_client.decorators import get, post


# 配置日志输出为debug级别
logging.basicConfig(level=logging.DEBUG)


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


def test_sync_client_with_mock_requests():
    """使用requests_mock测试同步客户端的mock功能"""
    with requests_mock.Mocker() as m:
        # 客户端会尝试发送真实HTTP请求，但会被requests_mock拦截
        client = TestClient(base_url="https://example.com")
        
        # 添加mock配置
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
        
        # 调用API方法，应该使用mock响应而不是发送HTTP请求
        users = client.get_users()
        
        # 验证mock响应
        assert isinstance(users, UserList)
        assert len(users.users) == 2
        assert users.users[0].name == "test1"
        assert users.users[1].name == "test2"
        assert users.total == 2
        
        # 验证没有实际发送HTTP请求
        assert not m.called
