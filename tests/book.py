from pydantic import BaseModel


class Book(BaseModel):
    name: str
    age: int


def get_the_book() -> Book:
    return Book(name="name", age=1)
