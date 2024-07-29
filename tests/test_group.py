from pydantic_client import Group
from pydantic_client.clients.requests import RequestsClient
from tests.book import Book, get_the_book

group = Group("/books")


class GroupClient(RequestsClient):
    @group.get("/{book_id}")
    def get(self, book_id: int) -> Book:  # type: ignore
        ...


def test_group_get(fastapi_server_url):

    client = GroupClient(fastapi_server_url)

    book = client.get(1)
    assert book == get_the_book()
