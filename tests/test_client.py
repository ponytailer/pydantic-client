import inspect

import pytest

from tests.book import Book, get_the_book


@pytest.mark.asyncio
async def test_get(clients):
    for cl in clients:
        book = cl.get_book(1, "world")
        if inspect.isawaitable(book):
            book = await book
        assert book.name == "name"
        assert book.age == 1


@pytest.mark.asyncio
async def test_get_num_pages(clients):
    for cl in clients:
        num_pages = cl.get_book_num_pages(1)
        if inspect.isawaitable(num_pages):
            num_pages = await num_pages
        assert num_pages == 40


@pytest.mark.asyncio
async def test_get_raw(clients):
    for cl in clients:
        book = cl.get_raw_book(1)
        if inspect.isawaitable(book):
            book = await book
        assert book["name"] == "name"
        assert book["age"] == 1


@pytest.mark.asyncio
async def test_post_form(clients):
    for cl in clients:
        book_to_send = Book(name="name", age=2)
        book = cl.create_book_form(book_to_send)
        if inspect.isawaitable(book):
            book = await book
        assert book == book_to_send


@pytest.mark.asyncio
async def test_put(clients):
    for cl in clients:
        book_to_send = Book(name="name", age=2)
        book = cl.change_book(1, book_to_send)
        if inspect.isawaitable(book):
            book = await book
        assert book == book_to_send


@pytest.mark.asyncio
async def test_delete(clients):
    for cl in clients:
        book = cl.delete_book(1)
        if inspect.isawaitable(book):
            book = await book
        assert book == get_the_book()


@pytest.mark.asyncio
async def test_patch(clients):
    for cl in clients:
        book_to_send = Book(name="name2", age=3)
        book = cl.patch_book(1, book_to_send)
        if inspect.isawaitable(book):
            book = await book
        assert book == book_to_send
