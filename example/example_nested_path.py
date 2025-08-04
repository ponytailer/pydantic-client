from typing import List, Optional
from pydantic import BaseModel
from pydantic_client import RequestsWebClient, get


class User(BaseModel):
    id: str
    name: str
    email: Optional[str] = None


class NestedPathClient(RequestsWebClient):
    @get("/users/complex", response_extract_path="$.data.users")
    def get_users_nested(self) -> List[User]:
        """
        Get users from a nested response structure where the users are in data.users
        
        Example response:
        {
            "status": "success",
            "data": {
                "users": [
                    {"id": "1", "name": "Alice", "email": "alice@example.com"},
                    {"id": "2", "name": "Bob", "email": "bob@example.com"}
                ],
                "total": 2
            }
        }
        """
        ...
    
    @get("/user/{user_id}", response_extract_path="data.user")
    def get_user_by_id(self, user_id: str) -> User:
        """
        Get a single user from a nested path
        
        Example response:
        {
            "status": "success",
            "data": {
                "user": {"id": "1", "name": "Alice", "email": "alice@example.com"}
            }
        }
        """
        ...
        
    @get("/search", response_extract_path="$.results[0]")
    def search_first_result(self) -> User:
        """
        Get just the first search result from an array
        
        Example response:
        {
            "query": "user search",
            "results": [
                {"id": "1", "name": "Alice", "email": "alice@example.com"},
                {"id": "2", "name": "Bob", "email": "bob@example.com"}
            ]
        }
        """
        ...


def main():
    """
    这是一个如何使用 response_extract_path 参数的示例。
    在实际应用中，您会调用真实的API。
    """
    # 创建客户端
    client = NestedPathClient(base_url="https://api.example.com")
    
    # 设置模拟响应，用于演示
    client.set_mock_config(mock_config=[
        {
            "name": "get_users_nested",
            "output": {
                "status": "success",
                "data": {
                    "users": [
                        {"id": "1", "name": "Alice", "email": "alice@example.com"},
                        {"id": "2", "name": "Bob", "email": "bob@example.com"}
                    ],
                    "total": 2
                }
            }
        },
        {
            "name": "get_user_by_id",
            "output": {
                "status": "success",
                "data": {
                    "user": {"id": "1", "name": "Alice", "email": "alice@example.com"}
                }
            }
        },
        {
            "name": "search_first_result",
            "output": {
                "query": "user search",
                "results": [
                    {"id": "1", "name": "Alice", "email": "alice@example.com"},
                    {"id": "2", "name": "Bob", "email": "bob@example.com"}
                ]
            }
        }
    ])
    
    # 获取嵌套结构中的所有用户
    users = client.get_users_nested()
    print(f"获取到 {len(users)} 个用户:")
    for user in users:
        print(f"  - {user.name} ({user.email})")
    
    # 通过ID获取单个用户
    user = client.get_user_by_id("1")
    print(f"\n获取用户: {user.name} ({user.id})")
    
    # 获取搜索结果的第一项
    first_result = client.search_first_result()
    print(f"\n第一个搜索结果: {first_result.name}")


if __name__ == "__main__":
    main()
