from example.protocol import BookProtocol, Book, AuthorProtocol, Author
from pydantic_client import pydantic_client_factory, ClientConfig

if __name__ == "__main__":
    cfg = ClientConfig(
        client_type="requests",
        base_url="https://example.com/api"
    )

    pydantic_client_factory.register(cfg)(BookProtocol)
    pydantic_client_factory.register(cfg)(AuthorProtocol)

    client = pydantic_client_factory.get_client(BookProtocol)
    book: Book = client.get_book(1, "name")

    author_client = pydantic_client_factory.get_client(AuthorProtocol)
    author: Author = author_client.get_author()
