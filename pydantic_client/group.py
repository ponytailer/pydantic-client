from typing import Optional

from .decorators import delete, get, patch, post, put


class Group:
    """
    Endpoint group.

    group = Group("/book", name="Book")
    person_group = Group("/person", name="Person")

    class R(RequestsClient):

        @group.get("/{book_id}")
        def get_book(self, book_id: int) -> Book:
            ...

        @group.post("/")
        def new_book(book: Book) -> Book:
            ...

        @person_group("/")
        def new_person(person: Person) -> Person:
            ...

    """

    def __init__(self, url_prefix: str, *, name: Optional[str] = None):
        self.url_prefix = url_prefix.rstrip("/")
        self.name = name

    def get(self, url: str):
        return get(self.url_prefix + url)

    def put(self, url: str, form_body: bool = False):
        return put(self.url_prefix + url, form_body=form_body)

    def post(self, url: str, form_body: bool = False):
        return post(self.url_prefix + url, form_body=form_body)

    def patch(self, url: str, form_body: bool = False):
        return patch(self.url_prefix + url, form_body=form_body)

    def delete(self, url: str):
        return delete(self.url_prefix + url)
