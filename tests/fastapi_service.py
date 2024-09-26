import json

from typing_extensions import Annotated

from fastapi import FastAPI, Form

from tests.book import Book, get_the_book

app = FastAPI()


@app.get("/books/{book_id}?query={query}")
async def get() -> Book:
    return get_the_book()


@app.get("/books/{book_id}")
def get_raw_book(book_id: int):
    return get_the_book()


@app.get("/books/{book_id}/num_pages")
def get_book_num_pages(book_id: int) -> str:
    return json.dumps(40)


@app.post("/books")
def create_book_form(name: Annotated[str, Form()], age: Annotated[int, Form()]) -> Book:
    return Book(name=name, age=age)


@app.put("/books/{book_id}")
def change_book(book_id: int, book: Book) -> Book:
    return book


@app.delete("/books/{book_id}")
def delete_book(book_id: int) -> Book:
    return get_the_book()


@app.patch("/books/{book_id}")
def patch_book(book_id: int, book: Book) -> Book:
    return book
