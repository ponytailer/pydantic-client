import pytest

from tests.conftest import R, HttpxR


@pytest.mark.asyncio
async def test_get(factory):
    book = factory.get_client(R).get_book(1, "world")
    assert book.name == "name"
    assert book.age == 1

    client = factory.get_client(HttpxR)
    book = await client.get_book(1, "world")
    assert book.name == "name"
    assert book.age == 1
