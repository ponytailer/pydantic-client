from pydantic import BaseModel


class Book(BaseModel):
    name: str
    age: int
