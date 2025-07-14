# Pydantic Client

[![codecov](https://codecov.io/gh/ponytailer/pydantic-client/branch/main/graph/badge.svg?token=CZX5V1YP22)](https://codecov.io/gh/ponytailer/pydantic-client)
[![Upload Python Package](https://github.com/ponytailer/pydantic-client/actions/workflows/python-publish.yml/badge.svg)](https://github.com/ponytailer/pydantic-client/actions/workflows/python-publish.yml)
[![PyPI version](https://badge.fury.io/py/pydantic-client.svg)](https://badge.fury.io/py/pydantic-client)
[![Python Version](https://img.shields.io/pypi/pyversions/pydantic-client.svg)](https://pypi.org/project/pydantic-client/)
[![Downloads](https://pepy.tech/badge/pydantic-client)](https://pepy.tech/project/pydantic-client)
[![License](https://img.shields.io/github/license/ponytailer/pydantic-client.svg)](https://github.com/ponytailer/pydantic-client/blob/main/LICENSE)

A flexible HTTP client library that leverages Pydantic models for request/response handling,
supporting both synchronous and asynchronous operations.

#### ⭐ If you like this project, please star it on GitHub!

## Features

- 🔥 **Type-safe**: Full type hints with Pydantic models for request/response validation
- 🚀 **Multiple HTTP backends**: Choose from `requests`, `aiohttp`, or `httpx`
- ⚡ **Async/Sync support**: Work with both synchronous and asynchronous HTTP operations
- 🎯 **Decorator-based API**: Clean, intuitive API definition with decorators
- 📝 **OpenAPI/Swagger support**: Generate client code from OpenAPI specifications
- 🛡️ **Automatic validation**: Request/response validation with Pydantic models
- ⚡ **Timing context manager**: Use `with client.span(prefix="myapi"):` to log timing for any API call, sync or async
- 🔧 **Flexible configuration**: Easy client configuration with headers, timeouts, and more
- 🔧 **convert api to llm tools**: API2Tools, support `agno`, others coming soon...

## TODO

- [ ] support langchain tools
- [ ] support crewai tools

## Installation

```bash
pip install pydantic-client
```

## Quick Start

```python
from pydantic import BaseModel
from pydantic_client import RequestsWebClient, get, post


# Define your response models
class UserResponse(BaseModel):
    id: int
    name: str
    email: str


class CreateUser(BaseModel):
    name: str
    email: str


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
    def create_user(self, user: CreateUser) -> UserResponse:
        pass

    @delete("/users", agno_tool=True, tool_description="this is the function to delete user")
    def delete_user(self, user_id: str):
        ...

session = requests.Session()


# Use the client
client = MyAPIClient(base_url="https://localhost")
user = client.get_user(user_id=123)

user_body = CreateUser(name="john", email="123@gmail.com")
user = client.create_user(user_body)

from agno.agent import Agent

agent = Agent(.....)
client.register_agno_tools(agent)  # delete_user is used by tools.

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

## Path Parameters

Path parameters are automatically extracted from the URL template and matched with method arguments:

```python
@get("users/{user_id}/posts/{post_id}")
def get_user_post(self, user_id: int, post_id: int) -> PostResponse:
    pass
```

## Request Parameters

- For GET and DELETE methods, remaining arguments are sent as query parameters
- For POST, PUT, and PATCH methods, remaining arguments are sent in the request body as JSON


### Timing Context Manager

All clients support a span context manager for simple API call timing and logging:

```python
with client.span(prefix="fetch_user"):
    user = client.get_user_by_id("123")
# Logs the elapsed time for the API call, useful for performance monitoring.
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

The library automatically validates responses against Pydantic models when specified as return types
in the method definitions.

## Error Handling

HTTP errors are raised as exceptions by the underlying HTTP client libraries. Make sure to handle
these appropriately in your application.
