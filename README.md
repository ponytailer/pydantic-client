# pydantic-client

[![codecov](https://codecov.io/gh/ponytailer/pydantic-client/branch/main/graph/badge.svg?token=CZX5V1YP22)](https://codecov.io/gh/ponytailer/pydantic-client) [![Upload Python Package](https://github.com/ponytailer/pydantic-client/actions/workflows/python-publish.yml/badge.svg)](https://github.com/ponytailer/pydantic-client/actions/workflows/python-publish.yml)

Http client base pydantic, with requests, aiohttp and httpx.

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

from pydantic_client import delete, get, post, put
from pydantic_client.clients.requests import RequestsClient


class Book(BaseModel):
    name: str
    age: int


class R(RequestsClient):

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


my_client = R("http://localhost/v1")
get_book: Book = my_client.get_book(1)
```

The Group

```python

from pydantic_client import Group
from pydantic_client.clients.requests import RequestsClient

group = Group("/book")
person_group = Group("/person")


class GroupClient(RequestsClient):
    def __init__(self):
        super().__init__("http://localhost")

    @group.get("/{book_id}")
    def get(self, book_id: int) -> Book:  # type: ignore
        ...

    @person_group.get("/{person_id}")
    def get_person(self, person_id: int) -> Person:  # type: ignore
        ...


client = GroupClient()
book = client.get(1)
person = client.get_person(1)


```

# change log

### v0.1.14: add global or request level headers

```python

# global level headers
my_client = R("http://localhost/v1", headers={"Authorization": "xxxxxxx"})

# request level headers, and its priority is higher than global. 

# header should be xxxxxxx
my_client.delete(1)
# header should be zzzzz
my_client.get(1, request_headers={"Authorization": "zzzzz"})
# header should be yyyyy
my_client.post(1, request_headers={"Authorization": "yyyyy"})
```

### v0.1.16: load config from toml to init client. 

```python

client = R.load_config_from_toml("config.toml")


```