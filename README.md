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

from pydantic_client import delete, get, post, put, pydantic_client_factory
from pydantic_client import ClientConfig


class Book(BaseModel):
    name: str
    age: int


@pydantic_client_factory.register(
    ClientConfig(
        client_type="requests",
        base_url="https://example.com",
        headers={"Authorization": "Bearer abcdefg"},
        timeout=10
    )
)
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


client = pydantic_client_factory.get_client()
book: Book = client.get_book(1)

```

And see the examples to get more examples.

# change log

### v1.0.0: refactor all the code, to be simple. remove the group client.

### v1.0.1: simple to use.
