import requests_mock
from typing import Optional
from pydantic import BaseModel
from pydantic_client import post, put, patch, RequestsWebClient


class User(BaseModel):
    id: str
    name: str
    email: Optional[str] = None


class UserCreateRequest(BaseModel):
    name: str
    email: Optional[str] = None


class TestFormBodyClient(RequestsWebClient):
    @post("/users")
    def create_user_json(self, user: UserCreateRequest) -> User:
        """Create user with JSON body using Pydantic model"""
        ...

    @post("/users", form_body=True)
    def create_user_form(self, user: UserCreateRequest) -> User:
        """Create user with form data using Pydantic model"""
        ...

    @post("/users/custom")
    def create_user_with_headers(self, user: UserCreateRequest, request_headers: dict) -> User:
        """Create user with custom headers"""
        ...


def test_pydantic_model_json_body():
    """Test that Pydantic models are correctly serialized to JSON body"""
    with requests_mock.Mocker() as m:
        # Mock the response
        m.post(
            'http://example.com/users',
            json={"id": "123", "name": "Test User", "email": "test@example.com"}
        )

        client = TestFormBodyClient(base_url="http://example.com")
        user_request = UserCreateRequest(name="Test User", email="test@example.com")
        response = client.create_user_json(user_request)

        # Verify the request was made with correct JSON body
        assert m.called
        assert m.last_request.json() == {"name": "Test User", "email": "test@example.com"}
        assert m.last_request.headers.get('content-type') == 'application/json'
        
        # Verify response
        assert isinstance(response, User)
        assert response.id == "123"


def test_pydantic_model_form_body():
    """Test that Pydantic models are correctly serialized to form data"""
    with requests_mock.Mocker() as m:
        # Mock the response
        m.post(
            'http://example.com/users',
            json={"id": "123", "name": "Test User", "email": "test@example.com"}
        )

        client = TestFormBodyClient(base_url="http://example.com")
        user_request = UserCreateRequest(name="Test User", email="test@example.com")
        response = client.create_user_form(user_request)

        # Verify the request was made with form data
        assert m.called
        # For form data, the body should be URL-encoded
        assert m.last_request.text == 'name=Test+User&email=test%40example.com'
        assert 'application/x-www-form-urlencoded' in m.last_request.headers.get('content-type', '')
        
        # Verify response
        assert isinstance(response, User)
        assert response.id == "123"


def test_custom_headers():
    """Test that custom headers are correctly passed"""
    with requests_mock.Mocker() as m:
        # Mock the response
        m.post(
            'http://example.com/users/custom',
            json={"id": "123", "name": "Test User", "email": "test@example.com"}
        )

        client = TestFormBodyClient(base_url="http://example.com")
        user_request = UserCreateRequest(name="Test User", email="test@example.com")
        custom_headers = {"X-Custom-Header": "custom-value", "Authorization": "Bearer token123"}
        
        response = client.create_user_with_headers(user_request, request_headers=custom_headers)

        # Verify the request was made with custom headers
        assert m.called
        assert m.last_request.headers.get('X-Custom-Header') == 'custom-value'
        assert m.last_request.headers.get('Authorization') == 'Bearer token123'
        
        # Verify response
        assert isinstance(response, User)
        assert response.id == "123"


def test_form_body_with_other_methods():
    """Test that form_body works with PUT and PATCH methods"""
    
    class TestFormMethodsClient(RequestsWebClient):
        @put("/users/{user_id}", form_body=True)
        def update_user_form(self, user_id: str, user: UserCreateRequest) -> User:
            ...

        @patch("/users/{user_id}", form_body=True)
        def patch_user_form(self, user_id: str, user: UserCreateRequest) -> User:
            ...

    with requests_mock.Mocker() as m:
        # Mock the responses
        m.put('http://example.com/users/123', json={"id": "123", "name": "Updated User", "email": "updated@example.com"})
        m.patch('http://example.com/users/123', json={"id": "123", "name": "Patched User", "email": "patched@example.com"})

        client = TestFormMethodsClient(base_url="http://example.com")
        user_request = UserCreateRequest(name="Test User", email="test@example.com")
        
        # Test PUT with form data
        response = client.update_user_form("123", user_request)
        assert m.called
        assert 'application/x-www-form-urlencoded' in m.last_request.headers.get('content-type', '')
        assert isinstance(response, User)
        
        # Test PATCH with form data  
        response = client.patch_user_form("123", user_request)
        assert 'application/x-www-form-urlencoded' in m.last_request.headers.get('content-type', '')
        assert isinstance(response, User)