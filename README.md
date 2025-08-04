# Pydantic Client

[![codecov](https://codecov.io/gh/ponytailer/pydantic-client/branch/main/graph/badge.svg?token=CZX5V1YP22)](https://codecov.io/gh/ponytailer/pydantic-client)
[![PyPI version](https://badge.fury.io/py/pydantic-client.svg)](https://badge.fury.io/py/pydantic-client)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://pypi.org/project/pydantic-client/)
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
- 🛡️ **Mock API Responses**: This is useful for testing or development purposes.
- ⚡ **Timing context manager**: Use `with client.span(prefix="myapi"):` to log timing for any API call, sync or async
- 🔧 **convert api to llm tools**: API2Tools, support `agno`, others coming soon...
- 🌟 **Nested Response Extraction**: Extract and parse deeply nested API responses using JSON path expressions

## TODO

- [ ] support langchain tools
- [ ] support crewai tools


## Installation

```bash
pip install pydantic-client
```


## Examples

See the [`example/`](./example/) directory for real-world usage of this library, including:

- `example_requests.py`: Synchronous usage with RequestsWebClient
- `example_httpx.py`: Async usage with HttpxWebClient
- `example_aiohttp.py`: Async usage with AiohttpWebClient
- `example_tools.py`: How to register and use Agno tools
- `example_nested_response.py`: How to extract data from nested API responses


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

    @get("/users/string?name={name}")
    def get_user_string(self, name: Optional[str] = None) -> dict:
        # will get raw json data
        ...
    
    @get("/users/{user_id}/bytes")
    def get_user_bytes(self, user_id: str) -> bytes:
        # will get raw content, bytes type.
        ...

    @delete(
        "/users",
        agno_tool=True,
        tool_description="description or use function annotation."
    )
    def delete_user(self, user_id: str, request_headers: Dict[str, Any]):
        ...


# Use the client
client = MyAPIClient(base_url="https://localhost")
user = client.get_user(user_id=123)

user_body = CreateUser(name="john", email="123@gmail.com")
user = client.create_user(user_body)

# will update the client headers.
client.delete_user("123", {"ba": "your"})


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

```python

# you can call signature by your self, overwrite the function `before_request`


class MyAPIClient(RequestsWebClient):
    # some code

    def before_request(self, request_params: Dict[str, Any]) -> Dict[str, Any]:
        # the request params before send: body, header, etc...
        sign = cal_signature(request_params)
        request_params["headers"].update(dict(signature=sign))
        return request_params


# will send your new request_params
user = client.get_user("123")

```

## Handling Nested API Responses

Many APIs return deeply nested JSON structures. Use the `response_extract_path` parameter to extract and parse specific data from complex API responses:

```python
from typing import List
from pydantic import BaseModel
from pydantic_client import RequestsWebClient, get

class User(BaseModel):
    id: str
    name: str
    email: str

class MyClient(RequestsWebClient):
    @get("/users/complex", response_extract_path="$.data.users")
    def get_users_nested(self) -> List[User]:
        """
        Extracts the users list from a nested response structure
        
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
        pass
    
    @get("/search", response_extract_path="$.results[0]")
    def search_first_result(self) -> User:
        """
        Get just the first search result from an array
        """
        pass
```

The `response_extract_path` parameter defines where to find the data in the response. It supports:
- Array indexing with square brackets: `$.results[0]` -> `User`
- Optional `$` prefix for root object: `$.data.users` -> `list[User]`

## Mock API Responses

You can configure the client to return mock responses instead of making actual API calls. This is useful for testing or development purposes.

### Setting Mock Responses Directly

```python
from pydantic_client import RequestsWebClient, get


class UserResponse(BaseModel):
    id: int
    name: str


class MyClient(RequestsWebClient):
    @get("/users/{user_id}")
    def get_user(self, user_id: int) -> UserResponse:
        pass

# Create client and configure mocks
client = MyClient(base_url="https://api.example.com")
client.set_mock_config(mock_config=[
    {
        "name": "get_user",
        "output": {
            "id": 123,
            "name": "Mock User"
        }
    }
])

# This will return the mock response without making an actual API call
user = client.get_user(1)  # Returns UserResponse(id=123, name="Mock User")
```

### Loading Mock Responses from a JSON File

You can also load mock configurations from a JSON file:

```python
# Load mock data from a JSON file
client.set_mock_config(mock_config_path="path/to/mock_data.json")
```

The JSON file should follow this format:

```json
[
    {
        "name": "get_user",
        "output": {
            "id": 123,
            "name": "Mock User"
        }
    },
    {
        "name": "list_users",
        "output": {
            "users": [
                {"id": 1, "name": "User 1"},
                {"id": 2, "name": "User 2"}
            ]
        }
    }
]
```

### Setting Mock Responses in Client Configuration

You can also include mock configuration when creating a client from configuration:

```python
config = {
    "base_url": "https://api.example.com",
    "timeout": 10,
    "mock_config": [
        {
            "name": "get_user",
            "output": {
                "id": 123,
                "name": "Mock User"
            }
        }
    ]
}

client = MyClient.from_config(config)
```

### Timing Context Manager

All clients support a span context manager for simple API call timing and logging:

```python
with client.span(prefix="fetch_user"):
    user = client.get_user_by_id("123")
# Logs the elapsed time for the API call, useful for performance monitoring.

# will send `fetch_user.elapsed` to statsd
client = MyAPIClient(base_url="https://localhost", statsd_address="localhost:8125")
with client.span(prefix="fetch_user"):
    user = client.get_user_by_id("123")

```

## Configuration

You can initialize clients with custom configurations:

```python
client = MyAPIClient(
    base_url="https://api.example.com",
    headers={"Custom-Header": "value"},
    session=requests.Session(),  # your own session
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
