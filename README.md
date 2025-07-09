# Pydantic Client

[![codecov](https://codecov.io/gh/ponytailer/pydantic-client/branch/main/graph/badge.svg?token=CZX5V1YP22)](https://codecov.io/gh/ponytailer/pydantic-client) [![Upload Python Package](https://github.com/ponytailer/pydantic-client/actions/workflows/python-publish.yml/badge.svg)](https://github.com/ponytailer/pydantic-client/actions/workflows/python-publish.yml)
[![PyPI version](https://badge.fury.io/py/pydantic-client.svg)](https://badge.fury.io/py/pydantic-client)
[![Python Version](https://img.shields.io/pypi/pyversions/pydantic-client.svg)](https://pypi.org/project/pydantic-client/)
[![Downloads](https://pepy.tech/badge/pydantic-client)](https://pepy.tech/project/pydantic-client)
[![License](https://img.shields.io/github/license/ponytailer/pydantic-client.svg)](https://github.com/ponytailer/pydantic-client/blob/main/LICENSE)


A flexible HTTP client library that leverages Pydantic models for request/response handling, supporting both synchronous and asynchronous operations.

## Features

- 🔥 **Type-safe**: Full type hints with Pydantic models for request/response validation
- 🚀 **Multiple HTTP backends**: Choose from `requests`, `aiohttp`, or `httpx`
- ⚡ **Async/Sync support**: Work with both synchronous and asynchronous HTTP operations
- 🎯 **Decorator-based API**: Clean, intuitive API definition with decorators
- 📝 **OpenAPI/Swagger support**: Generate client code from OpenAPI specifications
- 🛡️ **Automatic validation**: Request/response validation with Pydantic models
- 🔧 **Flexible configuration**: Easy client configuration with headers, timeouts, and more

## Installation

```bash
pip install pydantic-client
```

## Quick Start

```python
from typing import List
from pydantic import BaseModel
from pydantic_client import RequestsWebClient, get, post, put

# Define your response models
class UserResponse(BaseModel):
    id: int
    name: str
    email: str

class UserCreate(BaseModel):
    name: str
    email: str
    age: int

class UserUpdate(BaseModel):
    name: str
    email: str
    age: int

# Create your API client
class MyAPIClient(RequestsWebClient):
    def __init__(self):
        super().__init__(
            base_url="https://api.example.com",
            headers={"Authorization": "Bearer token"}
        )
    
    @get("users/{user_id}")
    def get_user(self, user_id: int) -> UserResponse:
        pass

    @post("users")
    def create_user(self, name: str, email: str) -> UserResponse:
        pass

# Use the client
client = MyAPIClient()
user = client.get_user(user_id=123)
```

## Available Clients

- `RequestsWebClient`: Synchronous client using the requests library
- `AiohttpWebClient`: Asynchronous client using aiohttp
- `HttpxWebClient`: Asynchronous client using httpx

## HTTP Method Decorators

The library provides decorators for common HTTP methods:

- `@get(path)`
- `@post(path)`
- `@put(path)`
- `@patch(path)`
- `@delete(path)`

## Request Parameters

The library supports several ways to pass parameters:

1. Path Parameters:
```python
@get("users/{user_id}")
def get_user(self, user_id: int) -> UserResponse:
    pass
```

2. Query Parameters (for GET and DELETE methods):
```python
@get("users")
def list_users(self, page: int, limit: int = 10) -> List[UserResponse]:
    pass
```

3. Pydantic Models as JSON Body (for POST, PUT, and PATCH methods):
```python
class UserCreate(BaseModel):
    name: str
    email: str
    age: int

@post("users")
def create_user(self, user: UserCreate) -> UserResponse:
    pass
```

4. Form Data with Pydantic Models:
```python
@post("users", form_body=True)
def create_user_form(self, user: UserCreate) -> UserResponse:
    # Will send the data as form-data instead of JSON
    pass
```

5. Mixed Parameters:
```python
@put("users/{user_id}")
def update_user(self, user_id: int, user: UserUpdate) -> UserResponse:
    # user_id will be used in the URL path
    # user will be serialized as the request body
    pass
```

You can also provide custom headers for specific requests:
```python
@post("users")
def create_user(self, user: UserCreate, request_headers: dict = None) -> UserResponse:
    # request_headers will be merged with client's default headers
    pass
```

## Configuration

You can initialize clients with custom configurations:

```python
client = MyAPIClient(
    base_url="https://api.example.com",
    headers={"Custom-Header": "value"},
    timeout=30  # in seconds
)

# Or using configuration dictionary
config = {
    "base_url": "https://api.example.com",
    "headers": {"Custom-Header": "value"},
    "timeout": 30
}
client = MyAPIClient.from_config(config)
```

## Type Safety

The library automatically validates responses against Pydantic models when specified as return types in the method definitions.

## Error Handling

HTTP errors are raised as exceptions by the underlying HTTP client libraries. Make sure to handle these appropriately in your application.

---

⭐ If you like this project, please star it on GitHub!
