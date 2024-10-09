from example.protocol import BookProtocol, Book, AuthorProtocol, Author
from pydantic_client import pydantic_client_manager, ClientConfig, ClientType


def get_book():
    cfg = ClientConfig(
        base_url="https://example.com/api"
    )
    pydantic_client_manager.register(cfg)(BookProtocol)
    client = pydantic_client_manager.get(BookProtocol)
    book: Book = client.get_book(1, "name")
    print(book)


async def get_author():
    cfg_2 = ClientConfig(
        client_type=ClientType.httpx,
        base_url="https://example.com/api"
    )

    pydantic_client_manager.register(cfg_2)(AuthorProtocol)

    author_client = pydantic_client_manager.get(AuthorProtocol)
    author: Author = await author_client.get_author()
    print(author)
