# pydantic-client

[![codecov](https://codecov.io/gh/ponytailer/pydantic-client/branch/main/graph/badge.svg?token=CZX5V1YP22)](https://codecov.io/gh/ponytailer/pydantic-client) [![Upload Python Package](https://github.com/ponytailer/pydantic-client/actions/workflows/python-publish.yml/badge.svg)](https://github.com/ponytailer/pydantic-client/actions/workflows/python-publish.yml)

A modern HTTP client library built on top of Pydantic for seamless API interaction with automatic validation and serialization. Supports both synchronous and asynchronous operations with multiple HTTP client backends.

## Features

- 🔥 **Type-safe**: Full type hints with Pydantic models for request/response validation
- 🚀 **Multiple HTTP backends**: Choose from `requests`, `aiohttp`, or `httpx`
- ⚡ **Async/Sync support**: Work with both synchronous and asynchronous HTTP operations
- 🎯 **Decorator-based API**: Clean, intuitive API definition with decorators
- 📝 **OpenAPI/Swagger support**: Generate client code from OpenAPI specifications
- 🛡️ **Automatic validation**: Request/response validation with Pydantic models
- 🔧 **Flexible configuration**: Easy client configuration with headers, timeouts, and more

## Installation

Choose the installation that matches your HTTP client preference:

### Basic Installation (requests only)
```bash
pip install pydantic-client
```

### With aiohttp support
```bash
pip install "pydantic-client[aiohttp]"
```

### With httpx support
```bash
pip install "pydantic-client[httpx]"
```

### All HTTP clients
```bash
pip install "pydantic-client[all]"
```

## Quick Start

### Synchronous Client (requests)

```python
from pydantic import BaseModel
from pydantic_client import RequestsWebClient, get, post

class User(BaseModel):
    id: int
    name: str
    email: str

class UserCreate(BaseModel):
    name: str
    email: str

class APIClient(RequestsWebClient):
    @get("/users/{user_id}")
    def get_user(self, user_id: int) -> User:
        """Get user by ID"""
        ...

    @post("/users")
    def create_user(self, user: UserCreate) -> User:
        """Create a new user"""
        ...

# Initialize client
client = APIClient(
    base_url="https://api.example.com",
    headers={"Authorization": "Bearer your-token"},
    timeout=30
)

# Use the client
user = client.get_user(123)
new_user = client.create_user(UserCreate(name="John", email="john@example.com"))
```

### Asynchronous Client (aiohttp)

```python
import asyncio
from pydantic_client import AiohttpWebClient, get, post

class AsyncAPIClient(AiohttpWebClient):
    @get("/users/{user_id}")
    async def get_user(self, user_id: int) -> User:
        """Get user by ID"""
        ...

    @post("/users")
    async def create_user(self, user: UserCreate) -> User:
        """Create a new user"""
        ...

async def main():
    client = AsyncAPIClient(
        base_url="https://api.example.com",
        headers={"Authorization": "Bearer your-token"}
    )
    
    user = await client.get_user(123)
    new_user = await client.create_user(UserCreate(name="Jane", email="jane@example.com"))

asyncio.run(main())
```

### Asynchronous Client (httpx)

```python
import asyncio
from pydantic_client import HttpxWebClient, get, post

class HttpxAPIClient(HttpxWebClient):
    @get("/users/{user_id}")
    async def get_user(self, user_id: int) -> User:
        """Get user by ID"""
        ...

    @post("/users")
    async def create_user(self, user: UserCreate) -> User:
        """Create a new user"""
        ...

async def main():
    client = HttpxAPIClient(
        base_url="https://api.example.com",
        headers={"Authorization": "Bearer your-token"}
    )
    
    user = await client.get_user(123)
    new_user = await client.create_user(UserCreate(name="Bob", email="bob@example.com"))

asyncio.run(main())
```

## API Documentation

### Client Classes

#### BaseWebClient
The abstract base class for all HTTP clients.

```python
class BaseWebClient:
    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30
    )
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'BaseWebClient':
        """Create client from configuration dictionary"""
        ...
```

#### RequestsWebClient
Synchronous HTTP client using the `requests` library.

```python
from pydantic_client import RequestsWebClient

class MyClient(RequestsWebClient):
    # Define your API methods here
    pass
```

#### AiohttpWebClient
Asynchronous HTTP client using the `aiohttp` library.

```python
from pydantic_client import AiohttpWebClient

class MyAsyncClient(AiohttpWebClient):
    # Define your async API methods here
    pass
```

#### HttpxWebClient
Asynchronous HTTP client using the `httpx` library with HTTP/2 support.

```python
from pydantic_client import HttpxWebClient

class MyHttpxClient(HttpxWebClient):
    # Define your async API methods here
    pass
```

### Decorators

#### @get(path)
Define a GET endpoint.

```python
@get("/users/{user_id}")
def get_user(self, user_id: int) -> User:
    ...
```

#### @post(path)
Define a POST endpoint.

```python
@post("/users")
def create_user(self, user: UserCreate) -> User:
    ...
```

#### @put(path)
Define a PUT endpoint.

```python
@put("/users/{user_id}")
def update_user(self, user_id: int, user: UserUpdate) -> User:
    ...
```

#### @delete(path)
Define a DELETE endpoint.

```python
@delete("/users/{user_id}")
def delete_user(self, user_id: int) -> None:
    ...
```

#### @patch(path)
Define a PATCH endpoint.

```python
@patch("/users/{user_id}")
def patch_user(self, user_id: int, user: UserPatch) -> User:
    ...
```

### Path Parameters and Query Parameters

Path parameters are automatically extracted from the URL path:

```python
@get("/users/{user_id}/posts/{post_id}")
def get_user_post(self, user_id: int, post_id: int) -> Post:
    ...
```

Query parameters are passed as additional function arguments:

```python
@get("/users")
def list_users(self, limit: int = 10, offset: int = 0) -> List[User]:
    ...
```

### Configuration

Create clients with custom configuration:

```python
# Using constructor
client = RequestsWebClient(
    base_url="https://api.example.com",
    headers={"Authorization": "Bearer token"},
    timeout=60
)

# Using from_config
config = {
    "base_url": "https://api.example.com",
    "headers": {"Authorization": "Bearer token"},
    "timeout": 60
}
client = RequestsWebClient.from_config(config)
```

## CLI Tool

Generate client code from OpenAPI/Swagger specifications:

```python
from pydantic_client.cli import parse

# Generate models and client code
parse("your-swagger-file.yaml", "generated_client.py")
```

This will generate Pydantic models and client code based on your OpenAPI specification and save it to the specified output file.

### Example Generated Code

```python
from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: Optional[str] = None

class UserCreate(BaseModel):
    name: str
    email: str

class APIClient:
    @get("/users/{user_id}")
    def get_user(self, user_id: int) -> User:
        ...

    @post("/users")
    def create_user(self, user: UserCreate) -> User:
        ...
```

## Advanced Usage

### Custom Headers per Request

```python
class APIClient(RequestsWebClient):
    @get("/users/{user_id}")
    def get_user(self, user_id: int, headers: Optional[Dict[str, str]] = None) -> User:
        ...

# Usage
client = APIClient(base_url="https://api.example.com")
user = client.get_user(123, headers={"X-Custom-Header": "value"})
```

### Error Handling

```python
from pydantic_client import RequestsWebClient, get
import requests

class APIClient(RequestsWebClient):
    @get("/users/{user_id}")
    def get_user(self, user_id: int) -> User:
        ...

client = APIClient(base_url="https://api.example.com")

try:
    user = client.get_user(123)
except requests.HTTPError as e:
    print(f"HTTP error: {e}")
except Exception as e:
    print(f"Other error: {e}")
```

### File Downloads

For binary content like files, the response will be returned as bytes:

```python
@get("/files/{file_id}/download")
def download_file(self, file_id: int) -> bytes:
    ...
```

## Examples

Check the `example/` directory for more complete examples:

- `example.py` - Basic usage with all three HTTP clients

## Requirements

- Python 3.9+
- pydantic >= 2.1
- requests (always installed)
- aiohttp (optional, for async support)
- httpx (optional, for async support with HTTP/2)

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/ponytailer/pydantic-client.git
cd pydantic-client
```

2. Install dependencies:
```bash
pip install -e ".[all]"
pip install pytest pytest-cov requests-mock pytest-aiohttp
```

3. Run tests:
```bash
pytest
```

### Guidelines

- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation for any API changes
- Make sure all tests pass before submitting

### Reporting Issues

Please use the [GitHub issue tracker](https://github.com/ponytailer/pydantic-client/issues) to report bugs or request features.

---

⭐ If you like this project, please star it on GitHub!
