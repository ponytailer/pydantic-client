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
    This is an example of how to use the response_extract_path parameter.
    In a real application, you would make actual API calls.
    """
    # Create client
    client = NestedPathClient(base_url="https://api.example.com")
    
    # Setup mock responses for demonstration
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
    
    # Get all users from a nested structure
    users = client.get_users_nested()
    print(f"Got {len(users)} users:")
    for user in users:
        print(f"  - {user.name} ({user.email})")
    
    # Get a single user by ID
    user = client.get_user_by_id("1")
    print(f"\nGot user: {user.name} ({user.id})")
    
    # Get just the first search result
    first_result = client.search_first_result()
    print(f"\nFirst search result: {first_result.name}")


if __name__ == "__main__":
    main()
