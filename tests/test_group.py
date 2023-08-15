from pydantic_client import Group
from pydantic_client.clients.requests import RequestsClient
from tests.book import Book
from tests.helpers import mock_requests

group = Group("/book")


class GroupClient(RequestsClient):
    def __init__(self):
        super().__init__("http://localhost")

    @group.get("/{book_id}")
    def get(self, book_id: int) -> Book:  # type: ignore
        ...


def test_group_get(monkeypatch):
    mock_resp = {"name": "name", "age": 1}
    mock_requests(monkeypatch, response=mock_resp)

    client = GroupClient()

    book = client.get(1)
    assert book.name == "name"
    assert book.age == 1
