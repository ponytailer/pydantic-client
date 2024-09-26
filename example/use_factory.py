from example.protocol import AuthorProtocol, BookProtocol, Book, Author
from pydantic_client import PydanticClientFactory
from pydantic_client.clients import RequestsClient, HttpxClient

if __name__ == '__main__':
    factory = PydanticClientFactory.from_toml("pydantic_client.toml") \
        .register_client("book_client", RequestsClient, BookProtocol) \
        .register_client("author_client", HttpxClient, AuthorProtocol) \
        .build()

    book: Book = factory.get_client(BookProtocol).get_book(1, "name")
    author: Author = factory.get_client(AuthorProtocol).get_author()
