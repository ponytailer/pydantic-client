# pydantic-client
[![codecov](https://codecov.io/gh/ponytailer/pydantic-client/branch/main/graph/badge.svg?token=CZX5V1YP22)](https://codecov.io/gh/ponytailer/pydantic-client)

Http client base pydantic, with requests or aiohttp

### How to use

```python



from pydantic import BaseModel

from pydantic_client import delete, get, post, put, RequestsClient


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
