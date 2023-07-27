# pydantic-client
Http client base pydantic, with requests or aiohttp

### How to use

```python
from typing import List

import requests
from pydantic import BaseModel

from pydantic_client import RequestsClient, rest


class Book(BaseModel):
    name: str
    address: str


class Books(BaseModel):
    books: List[Book]


class MyClient(RequestsClient):

    @rest("/books?name={name}")
    def get_books(self, name: str) -> Books:
        ...

    @rest("/books/{book_id}")
    def get_book(self, book_id: int) -> Book:
        ...

    @rest("/books", method="POST")
    def create_book(self, book: Book) -> Book:
        ...


my_client = MyClient(requests.Session())
get_book: Book = my_client.get_book(1)
```