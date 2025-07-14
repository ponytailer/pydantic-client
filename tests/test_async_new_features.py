import pytest
from typing import Optional
from pydantic import BaseModel
from pydantic_client import post, AiohttpWebClient


class User(BaseModel):
    id: str
    name: str
    email: Optional[str] = None


class UserCreateRequest(BaseModel):
    name: str
    email: Optional[str] = None


class TestAsyncFormBodyClient(AiohttpWebClient):
    @post("/users")
    async def create_user_json(self, user: UserCreateRequest) -> User:
        """Create user with JSON body using Pydantic model"""
        ...

    @post("/users", form_body=True)
    async def create_user_form(self, user: UserCreateRequest) -> User:
        """Create user with form data using Pydantic model"""
        ...

    @post("/users/custom")
    async def create_user_with_headers(self, user: UserCreateRequest, request_headers: dict) -> User:
        """Create user with custom headers"""
        ...


@pytest.mark.asyncio
async def test_async_pydantic_model_json_body():
    """Test that async client correctly handles Pydantic models as JSON body"""
    # For this test, we'll use a simple mock by patching the _request method
    
    class MockAsyncClient(TestAsyncFormBodyClient):
        async def _request(self, request_info):
            # Verify that the correct parameters are passed
            assert request_info.method == "POST"
            assert request_info.path == "/users"
            assert request_info.json == {"name": "Test User", "email": "test@example.com"}
            assert request_info.data is None  # Should be None for JSON requests
            
            # Return mock response
            return {"id": "123", "name": "Test User", "email": "test@example.com"}

    client = MockAsyncClient(base_url="http://example.com")
    user_request = UserCreateRequest(name="Test User", email="test@example.com")
    response = await client.create_user_json(user_request)

    assert response["id"] == "123"


@pytest.mark.asyncio
async def test_async_pydantic_model_form_body():
    """Test that async client correctly handles Pydantic models as form data"""
    
    class MockAsyncClient(TestAsyncFormBodyClient):
        async def _request(self, request_info):
            # Verify that the correct parameters are passed
            assert request_info.method == "POST"
            assert request_info.path == "/users"
            assert request_info.data == {"name": "Test User", "email": "test@example.com"}
            assert request_info.json is None  # Should be None for form requests
            
            # Return mock response
            return {"id": "123", "name": "Test User", "email": "test@example.com"}

    client = MockAsyncClient(base_url="http://example.com")
    user_request = UserCreateRequest(name="Test User", email="test@example.com")
    response = await client.create_user_form(user_request)

    assert response["id"] == "123"


@pytest.mark.asyncio
async def test_async_custom_headers():
    """Test that async client correctly handles custom headers"""
    
    class MockAsyncClient(TestAsyncFormBodyClient):
        async def _request(self, request_info):
            # Verify that the correct parameters are passed
            assert request_info.method == "POST"
            assert request_info.path == "/users/custom"
            assert request_info.headers == {"X-Custom-Header": "custom-value", "Authorization": "Bearer token123"}
            
            # Return mock response
            return {"id": "123", "name": "Test User", "email": "test@example.com"}

    client = MockAsyncClient(base_url="http://example.com")
    user_request = UserCreateRequest(name="Test User", email="test@example.com")
    custom_headers = {"X-Custom-Header": "custom-value", "Authorization": "Bearer token123"}
    
    response = await client.create_user_with_headers(user_request, request_headers=custom_headers)

    assert response["id"] == "123"