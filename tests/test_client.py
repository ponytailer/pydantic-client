import unittest

from pydantic import BaseModel

from pydantic_client import delete, get, post, put, RequestsClient


class Book(BaseModel):
    name: str
    age: int


class R(RequestsClient):
    def __init__(self):
        super().__init__("http://localhost")

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


class TestClient(unittest.TestCase):

    def setUp(self):
        self.test_client = R()

    def tearDown(self):
        self.test_client = None

    def test_get(self):
        ...
