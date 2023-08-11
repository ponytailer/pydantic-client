import pytest

from tests.book import Book
from tests.helpers import mock_aio_http, mock_httpx


@pytest.fixture
def mock_book(monkeypatch):
    mock_resp = {"name": "name", "age": 1}
    yield mock_aio_http(monkeypatch, response=mock_resp)


@pytest.fixture
def mock_httpx_book(monkeypatch):
    mock_resp = {"name": "name", "age": 1}
    yield mock_httpx(monkeypatch, response=mock_resp)


@pytest.mark.asyncio
async def test_get(async_client, httpx_client, mock_book, mock_httpx_book):
    book: Book = await async_client.get_book(1, "world")
    assert book.name == "name"
    assert book.age == 1

    book: Book = await httpx_client.get_book(1, "world")
    assert book.name == "name"
    assert book.age == 1


@pytest.mark.asyncio
async def test_get_raw(async_client, httpx_client, mock_book, mock_httpx_book):
    book: dict = await async_client.get_raw_book(1)
    assert book["name"] == "name"
    assert book["age"] == 1

    book: dict = await httpx_client.get_raw_book(1)
    assert book["name"] == "name"
    assert book["age"] == 1


@pytest.mark.asyncio
async def test_post_form(async_client, httpx_client, mock_book, mock_httpx_book):
    book: Book = await async_client.create_book_form(Book(name="name", age=2))
    assert book.name == "name"
    assert book.age == 1

    book: Book = await httpx_client.create_book_form(Book(name="name", age=2))
    assert book.name == "name"
    assert book.age == 1


@pytest.mark.asyncio
async def test_put(async_client, httpx_client, mock_book, mock_httpx_book):
    book: Book = await async_client.change_book(1, Book(name="name", age=2))
    assert book.name == "name"
    assert book.age == 1

    book: Book = await httpx_client.change_book(1, Book(name="name", age=2))
    assert book.name == "name"
    assert book.age == 1


@pytest.mark.asyncio
async def test_delete(async_client, httpx_client, mock_book, mock_httpx_book):
    book: Book = await async_client.delete_book(1)
    assert book.name == "name"
    assert book.age == 1

    book: Book = await httpx_client.delete_book(1)
    assert book.name == "name"
    assert book.age == 1
