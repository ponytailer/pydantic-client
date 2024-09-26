# pydantic-client

[![codecov](https://codecov.io/gh/ponytailer/pydantic-client/branch/main/graph/badge.svg?token=CZX5V1YP22)](https://codecov.io/gh/ponytailer/pydantic-client) [![Upload Python Package](https://github.com/ponytailer/pydantic-client/actions/workflows/python-publish.yml/badge.svg)](https://github.com/ponytailer/pydantic-client/actions/workflows/python-publish.yml)

Http client base pydantic, with requests, aiohttp and httpx.
Only support the json response.

### How to install

> only support `requests`:
>> pip install pydantic-client

> support `aiohttp` and `requests`:
>> pip install "pydantic-client[aiohttp]"

> support `httpx(async)` and `requests`:
>> pip install "pydantic-client[httpx]"

> support all:
>> pip install "pydantic-client[all]"

### How to use

```python
from pydantic import BaseModel

from pydantic_client import delete, get, post, put, PydanticClient
from pydantic_client.clients import RequestsClient, AIOHttpClient, HttpxClient
from pydantic_client import ClientConfig, PydanticClientFactory


class Book(BaseModel):
    name: str
    age: int


class WebClient:

    @get("/books/{book_id}?query={query}")
    def get_book(self, book_id: int, query: str) -> Book:
        ...

    @post("/books", form_body=True)
    def create_book_form(self, book: Book) -> Book:
        """ will post the form with book"""
        ...

    @put("/books/{book_id}")
    def change_book(self, book_id: int, book: Book) -> Book:
        """will put the json body"""
        ...

    @delete("/books/{book_id}")
    def change_book(self, book_id: int) -> Book:
        ...

"""
toml config example:

[tools.pydantic-client.config]
base_url = "http://localhost:5000" (have to set)
headers.authorization = "Bearer xxxxxx" (optional)
http2 = true  (optional)
timeout = 10 (optional)
"""


client = PydanticClient.from_toml("your_toml_path.toml") \
    .bind_client(RequestsClient) \
    .bind_protocol(WebClient) \
    .build()

# or

client: WebClient = PydanticClient(
    ClientConfig(
        base_url="https://example.com",
        headers={"Authorization": "Bearer abcdefg"},
        timeout=10
    )
).bind_client(RequestsClient) \
    .bind_protocol(WebClient) \
    .build()


get_book: Book = client.get_book(1)

# use the factory

"""
toml file example:
[[tools.pydantic_client.factory]]
name = "book_client
base_url = "https://example.com/api/v1"
timeout = 1
[[tools.pydantic_client.factory]]
name = "author_client
base_url = "https://example.com/api/v2"
timeout = 1
[[tools.pydantic_client.factory]]
name = "address_client
base_url = "https://example.com/api/v3"
timeout = 1
"""

class BookProtocol:
    @get("/books/{book_id}?query={query}")
    def get_book(self, book_id: int, query: str) -> Book:
        ...
    
class AuthorProtocol:
    @get("/books/{book_id}?query={query}")
    def get_book(self, book_id: int, query: str) -> Book:
        ...
    
class AddressProtocol:
    @get("/books/{book_id}?query={query}")
    def get_book(self, book_id: int, query: str) -> Book:
        ...

factory = PydanticClientFactory.from_toml("pydantic_client.toml") \
    .register_client("book_client", RequestsClient, BookProtocol) \
    .register_client("author_client", HttpxClient, AuthorProtocol) \
    .register_client("address_client", AIOHttpClient, AddressProtocol) \
    .build()

book: Book = factory.get_client(BookProtocol).get_book(1, "name")
author: Book = factory.get_client(AuthorProtocol).get_book(1, "name")
```

# change log

### v1.0.0: refactor all the code, to be simple. remove the group client.

factory = PydanticClientFactory.from_toml("pydantic_client.toml") \
    .register_client("book_client", RequestsClient, BookProtocol) \
    .register_client("author_client", HttpxClient, AuthorProtocol) \
    .register_client("address_client", AIOHttpClient, AddressProtocol) \
    .build()

book: Book = factory.get_client(BookProtocol).get_books(1)
```

# change log

### v1.0.0: refactor all the code, to be simple. remove the group client.
