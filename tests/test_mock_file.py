import os
import pytest
from typing import List, Optional
from pydantic import BaseModel

from pydantic_client.sync_client import RequestsWebClient
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
class FileTestClient(RequestsWebClient):
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


def test_mock_from_file():
    """测试从文件加载mock配置"""
    client = FileTestClient(base_url="https://example.com")
    
    # 获取mock_data.json的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    mock_file_path = os.path.join(current_dir, "mock_data.json")
    
    # 从文件加载mock配置
    client.set_mock_config(mock_config_path=mock_file_path)
    
    # 验证mock响应 - 使用从文件加载的数据
    users = client.get_users()
    assert isinstance(users, UserList)
    assert len(users.users) == 2
    assert users.users[0].name == "file_user1"
    assert users.users[1].name == "file_user2"
    assert users.total == 2
    
    user = client.get_user(1)
    assert isinstance(user, User)
    assert user.name == "file_user"
    assert user.age == 35
    assert user.email == "file_user@example.com"


def test_mock_file_and_config():
    """测试同时提供文件和配置列表时，优先使用配置列表"""
    client = FileTestClient(base_url="https://example.com")
    
    # 获取mock_data.json的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    mock_file_path = os.path.join(current_dir, "mock_data.json")
    
    # 提供直接配置和文件路径
    direct_config = [
        {
            "name": "get_users",
            "output": {
                "users": [
                    {"name": "direct_user1", "age": 40, "email": "direct1@example.com"},
                    {"name": "direct_user2", "age": 45, "email": "direct2@example.com"}
                ],
                "total": 2
            }
        }
    ]
    
    # 两者都提供时，应该使用直接配置
    client.set_mock_config(mock_config_path=mock_file_path, mock_config=direct_config)
    
    # 验证mock响应 - 应该使用直接配置的数据
    users = client.get_users()
    assert isinstance(users, UserList)
    assert len(users.users) == 2
    assert users.users[0].name == "file_user1"  # 使用file_config中的数据
    assert users.users[1].name == "file_user2"
    

def test_mock_file_not_found():
    """测试文件不存在的情况"""
    client = FileTestClient(base_url="https://example.com")
    
    # 指定一个不存在的文件路径
    non_existent_path = "/path/to/non_existent_file.json"
    
    # 应该抛出FileNotFoundError异常
    with pytest.raises(FileNotFoundError):
        client.set_mock_config(mock_config_path=non_existent_path)
