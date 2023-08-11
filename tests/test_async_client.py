import pytest

from tests.book import Book
from tests.helpers import mock_aio_http


@pytest.fixture
def mock_get_book(monkeypatch):
    mock_resp = {"name": "name", "age": 1}
    yield mock_aio_http(monkeypatch, response=mock_resp)


@pytest.mark.asyncio
async def test_get(async_client, mock_get_book):
    book: Book = await async_client.get_book(1, "world")
    assert book.name == "name"
    assert book.age == 1


@pytest.mark.asyncio
async def test_get_raw(async_client, mock_get_book):
    book: dict = await async_client.get_raw_book(1)
    assert book["name"] == "name"
    assert book["age"] == 1


@pytest.mark.asyncio
async def test_post_form(async_client, mock_get_book):
    book: Book = await async_client.create_book_form(Book(name="name", age=2))
    assert book.name == "name"
    assert book.age == 1


@pytest.mark.asyncio
async def test_put(async_client, mock_get_book):
    book: Book = await async_client.change_book(1, Book(name="name", age=2))
    assert book.name == "name"
    assert book.age == 1


@pytest.mark.asyncio
async def test_delete(async_client, mock_get_book):
    book: Book = await async_client.delete_book(1)
    assert book.name == "name"
    assert book.age == 1
