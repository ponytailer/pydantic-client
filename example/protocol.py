from pydantic import BaseModel

from pydantic_client import get, post, put, delete


class Book(BaseModel):
    name: str
    year: int


class Author(BaseModel):
    name: str


class BookProtocol:

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


class AuthorProtocol:

    @get("/authors")
    def get_author(self) -> Author:
        ...
