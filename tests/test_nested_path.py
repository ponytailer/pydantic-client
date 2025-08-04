import pytest
import requests_mock
from typing import Optional, List

from pydantic import BaseModel
from pydantic_client import RequestsWebClient, get


class User(BaseModel):
    id: str
    name: str
    email: Optional[str] = None


class UserList(BaseModel):
    users: List[User]


class NestedResponseTestClient(RequestsWebClient):
    @get("/users/complex", response_extract_path="$.data.users")
    def get_users_nested(self) -> List[User]:
        """Get users from a nested response structure"""
        ...

    @get("/users/paginated", response_extract_path="$.data.items")
    def get_paginated_users(self) -> List[User]:
        """Get users from paginated response"""
        ...
        
    @get("/users/deep/structure", response_extract_path="data.result.user")
    def get_deeply_nested_user(self) -> User:
        """Get a deeply nested single user"""
        ...
        
    @get("/users/first", response_extract_path="$.data.users[0]")
    def get_first_user(self) -> User:
        """Get the first user from an array"""
        ...


@pytest.fixture
def client():
    return NestedResponseTestClient(base_url="https://api.example.com")


def test_nested_response_extraction(client):
    with requests_mock.Mocker() as m:
        # 测试嵌套列表提取
        complex_response = {
            "status": "success",
            "code": 200,
            "data": {
                "users": [
                    {"id": "1", "name": "Alice", "email": "alice@example.com"},
                    {"id": "2", "name": "Bob", "email": "bob@example.com"}
                ],
                "total": 2
            }
        }
        m.get("https://api.example.com/users/complex", json=complex_response)
        
        result = client.get_users_nested()
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0].id == "1"
        assert result[0].name == "Alice"
        assert result[1].name == "Bob"
        
        # 测试分页数据提取
        paginated_response = {
            "data": {
                "items": [
                    {"id": "3", "name": "Charlie"},
                    {"id": "4", "name": "Dave"}
                ],
                "page": 1,
                "total_pages": 5
            },
            "meta": {
                "request_id": "abc-123"
            }
        }
        m.get("https://api.example.com/users/paginated", json=paginated_response)
        
        paginated_result = client.get_paginated_users()
        assert isinstance(paginated_result, list)
        assert len(paginated_result) == 2
        assert paginated_result[0].id == "3"
        assert paginated_result[0].name == "Charlie"
        assert paginated_result[1].name == "Dave"
        assert paginated_result[1].email is None  # 测试可选字段
        
        # 测试深层嵌套
        deep_response = {
            "data": {
                "result": {
                    "user": {
                        "id": "5", 
                        "name": "Eve",
                        "email": "eve@example.com"
                    }
                }
            }
        }
        m.get("https://api.example.com/users/deep/structure", json=deep_response)
        
        deep_result = client.get_deeply_nested_user()
        assert isinstance(deep_result, User)
        assert deep_result.id == "5"
        assert deep_result.name == "Eve"
        assert deep_result.email == "eve@example.com"
        
        # 测试数组索引
        array_response = {
            "data": {
                "users": [
                    {"id": "6", "name": "Frank", "email": "frank@example.com"},
                    {"id": "7", "name": "Grace", "email": "grace@example.com"}
                ]
            }
        }
        m.get("https://api.example.com/users/first", json=array_response)
        
        first_user = client.get_first_user()
        assert isinstance(first_user, User)
        assert first_user.id == "6"
        assert first_user.name == "Frank"


def test_nested_response_extraction_with_missing_data(client):
    with requests_mock.Mocker() as m:
        # 测试缺失数据
        invalid_response = {
            "status": "error",
            "message": "No data available"
        }
        m.get("https://api.example.com/users/complex", json=invalid_response)
        
        result = client.get_users_nested()
        assert result is None


def test_nested_response_with_mock_config():
    client = NestedResponseTestClient(base_url="https://api.example.com")
    
    # 设置mock配置
    client.set_mock_config(mock_config=[
        {
            "name": "get_users_nested",
            "output": {
                "data": {
                    "users": [
                        {"id": "mock1", "name": "MockUser1", "email": "mock1@example.com"},
                        {"id": "mock2", "name": "MockUser2", "email": "mock2@example.com"}
                    ]
                }
            }
        }
    ])
    
    # 测试mock数据
    result = client.get_users_nested()
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0].id == "mock1"
    assert result[0].name == "MockUser1"
    assert result[1].id == "mock2"
    assert result[1].name == "MockUser2"
