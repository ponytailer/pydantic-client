import pytest

from pydantic_client import delete, get, post, put
from pydantic_client.clients.aiohttp import AIOHttpClient
from pydantic_client.clients.httpx import HttpxClient
from pydantic_client.clients.requests import RequestsClient
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


class AsyncR(AIOHttpClient):
    def __init__(self):
        super().__init__("http://localhost")

    @get("/books/{book_id}?query={query}")
    async def get_book(self, book_id: int, query: str) -> Book:
        ...

    @get("/books/{book_id}")
    async def get_raw_book(self, book_id: int):
        ...

    @post("/books", form_body=True)
    async def create_book_form(self, book: Book) -> Book:
        """ will post the form with book"""
        ...

    @put("/books/{book_id}")
    async def change_book(self, book_id: int, book: Book) -> Book:
        """will put the json body"""
        ...

    @delete("/books/{book_id}")
    async def delete_book(self, book_id: int) -> Book:
        ...


class HttpxR(HttpxClient, AsyncR):
    ...


@pytest.fixture
def client():
    yield R()


@pytest.fixture
def async_client():
    yield AsyncR()


@pytest.fixture
def httpx_client():
    yield HttpxR("http://localhost")
