import pytest

from tests.book import Book
from tests.helpers import mock_requests


@pytest.fixture
def mock_get_book(monkeypatch):
    mock_resp = {"name": "name", "age": 1}
    yield mock_requests(monkeypatch, response=mock_resp)


def test_get(client, mock_get_book):
    book: Book = client.get_book(1, "world")
    assert book.name == "name"
    assert book.age == 1


def test_get_raw(client, mock_get_book):
    book: dict = client.get_raw_book(1)
    assert book["name"] == "name"
    assert book["age"] == 1


def test_post_form(client, mock_get_book):
    book: Book = client.create_book_form(Book(name="name", age=2))
    assert book.name == "name"
    assert book.age == 1


def test_put(client, mock_get_book):
    book: Book = client.change_book(1, Book(name="name", age=2))
    assert book.name == "name"
    assert book.age == 1


def test_delete(client, mock_get_book):
    book: Book = client.delete_book(1)
    assert book.name == "name"
    assert book.age == 1
