import inspect

import pytest

from tests.book import Book
from tests.helpers import mock_aio_http, mock_httpx, mock_requests


@pytest.fixture
def mock_book(monkeypatch):
    mock_resp = {"name": "name", "age": 1}
    yield (
        mock_aio_http(monkeypatch, response=mock_resp),
        mock_httpx(monkeypatch, response=mock_resp),
        mock_requests(monkeypatch, response=mock_resp)
    )


@pytest.mark.asyncio
async def test_get(clients, mock_book):
    for cl in clients:
        book = cl.get_book(1, "world")
        if inspect.isawaitable(book):
            book = await book
        assert book.name == "name"
        assert book.age == 1


@pytest.mark.asyncio
async def test_get_raw(clients, mock_book):
    for cl in clients:
        book = cl.get_raw_book(1)
        if inspect.isawaitable(book):
            book = await book
        assert book["name"] == "name"
        assert book["age"] == 1


@pytest.mark.asyncio
async def test_post_form(clients, mock_book):
    for cl in clients:
        book = cl.create_book_form(Book(name="name", age=2))
        if inspect.isawaitable(book):
            book = await book
        assert book.name == "name"
        assert book.age == 1


@pytest.mark.asyncio
async def test_put(clients, mock_book):
    for cl in clients:
        book = cl.change_book(1, Book(name="name", age=2))
        if inspect.isawaitable(book):
            book = await book
        assert book.name == "name"
        assert book.age == 1


@pytest.mark.asyncio
async def test_delete(clients, mock_book):
    for cl in clients:
        book = cl.delete_book(1)
        if inspect.isawaitable(book):
            book = await book
        assert book.name == "name"
        assert book.age == 1


@pytest.mark.asyncio
async def test_patch(clients, mock_book):
    for cl in clients:
        book = cl.patch_book(1, Book(name="name2", age=3))
        if inspect.isawaitable(book):
            book = await book
        assert book.name == "name"
        assert book.age == 1
