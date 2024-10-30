import pytest
import typing
from aiohttp import ClientSession
from httpx import AsyncClient
from requests import Session

from pydantic_client import delete, get, patch, post, put, \
    ClientConfig, pydantic_client_manager, ClientType
from pydantic_client.schema.file import File
from tests.book import Book

server_url = "http://localhost:12098"

config_1 = ClientConfig(
    base_url=server_url,
)

config_2 = ClientConfig(
    client_type=ClientType.httpx,
    base_url=server_url,
    timeout=10
)

config_3 = ClientConfig(
    client_type=ClientType.aiohttp,
    base_url=server_url,
    timeout=10
)

config_4 = ClientConfig(
    client_type=ClientType.aiohttp,
    base_url=server_url,
    timeout=10,
    client_session=lambda: ClientSession()
)

config_5 = ClientConfig(
    client_type=ClientType.httpx,
    base_url=server_url,
    timeout=10,
    client_session=lambda: AsyncClient()
)
config_6 = ClientConfig(
    client_type=ClientType.requests,
    base_url=server_url,
    timeout=10,
    client_session=lambda: Session()
)


@pydantic_client_manager.register(config_1)
class R:

    @get("/book_list")
    def get_books(self) -> typing.List:
        ...

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

    @post("/books/file")
    def download(self) -> File:
        ...


@pydantic_client_manager.register(config_3)
class AsyncR:

    @get("/book_list")
    async def get_books(self) -> typing.List:
        ...

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

    @post("/books/file")
    async def download(self) -> File:
        ...


@pydantic_client_manager.register(config_2)
class HttpxR(AsyncR):
    ...


@pydantic_client_manager.register(config_4)
class AsyncWithSession(AsyncR):
    ...


@pydantic_client_manager.register(config_5)
class HttpxWithSession(HttpxR):
    ...


@pydantic_client_manager.register(config_6)
class RequestsWithSession(R):
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
    client_1 = pydantic_client_manager.get(R)
    client_2 = pydantic_client_manager.get(AsyncR)
    client_3 = pydantic_client_manager.get(HttpxR)
    client_4 = pydantic_client_manager.get(AsyncWithSession)
    client_5 = pydantic_client_manager.get(HttpxWithSession)
    client_6 = pydantic_client_manager.get(RequestsWithSession)

    yield client_1, client_2, client_3, client_4, client_5, client_6
