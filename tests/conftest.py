import pytest

from pydantic_client import delete, get, patch, post, put, PydanticClient
from pydantic_client.clients.aiohttp import AIOHttpClient
from pydantic_client.clients.httpx import HttpxClient
from pydantic_client.clients.requests import RequestsClient
from tests.book import Book


class R:

    @get("/books/{book_id}?query={query}")
    def get_book(self, book_id: int, query: str) -> Book:
        ...

    @get("/books/{book_id}")
    def get_raw_book(self, book_id: int):
        ...

    @get("/books/{book_id}/num_pages")
    def get_book_num_pages(self, book_id: int) -> int:
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

    @patch("/books/{book_id}")
    def patch_book(self, book_id: int, book: Book) -> Book:
        ...


class AsyncR:
    @get("/books/{book_id}?query={query}")
    async def get_book(self, book_id: int, query: str) -> Book:
        ...

    @get("/books/{book_id}")
    async def get_raw_book(self, book_id: int):
        ...

    @get("/books/{book_id}/num_pages")
    async def get_book_num_pages(self, book_id: int) -> int:
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

    @patch("/books/{book_id}")
    async def patch_book(self, book_id: int, book: Book) -> Book:
        ...


class HttpxR(AsyncR):
    ...


@pytest.fixture(scope="session")
def fastapi_server_url() -> str:
    from uvicorn import run
    from .fastapi_service import app
    from threading import Thread
    host = "localhost"
    port = 12098  # TODO: add port availability check

    def start_server():
        run(app, host=host, port=port)

    thread = Thread(target=start_server, daemon=True)
    thread.start()

    for _ in range(10):
        assert thread.is_alive(), "Fastapi thread died"
        try:
            url = f"http://{host}:{port}"
            import requests
            book = requests.get(f"{url}/books/5")
            book.raise_for_status()
            return "http://localhost:12098/"
        except Exception:
            from time import sleep
            sleep(1)

    raise Exception("Can't start fastapi server in 10 seconds")


@pytest.fixture
def clients(fastapi_server_url):
    client_1 = PydanticClient.from_toml("tests/config.toml") \
        .bind_client(RequestsClient) \
        .bind_protocol(R).build()

    client_3 = PydanticClient.from_toml("tests/config.toml") \
        .bind_client(HttpxClient) \
        .bind_protocol(HttpxR).build()

    client_2 = PydanticClient.from_toml("tests/config.toml") \
        .bind_client(AIOHttpClient) \
        .bind_protocol(AsyncR).build()

    yield client_1, client_2, client_3
