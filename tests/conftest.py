import pytest

from pydantic_client import delete, get, post, put, RequestsClient
from tests.book import Book


class R(RequestsClient):
    def __init__(self):
        super().__init__("http://localhost")

    @get("/books/{book_id}?query={query}")
    def get_book(self, book_id: int, query: str) -> Book:
        ...

    @get("/books/{book_id}")
    def get_raw_book(self, book_id: int):
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
    def delete_book(self, book_id: int) -> Book:
        ...


@pytest.fixture
def client():
    yield R()
