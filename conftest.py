from typing import Any, Callable, Generator

import pytest
import logging
from src.api.config import api_config
from src.api.http_client import HTTPClient
from src.utils.factory import BookFactory

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def api_client():
    return HTTPClient(api_config.API_URL)


@pytest.fixture(autouse=True)
def clean_db(api_client: HTTPClient) -> Generator[None, Any, None]:
    yield

    try:
        api_client.clear_inventory()
        logger.info("Inventory cleared")
    except Exception as e:
        logger.error(f"Failed to clear inventory: {e}")

    books_response = api_client.get_books()
    for book in books_response.data.books:
        api_client.delete_book(book.id)
        logger.info(f"Deleted book: {book.id}")

    authors_response = api_client.get_authors()
    for author in authors_response.data.authors:
        api_client.delete_author(author.id)
        logger.info(f"Deleted author: {author.id}")


@pytest.fixture(scope="function")
def create_books(api_client: HTTPClient) -> Callable[..., list[Any]]:
    def _create_books(count: int = 1):
        books = [api_client.post_book(BookFactory.create_payload()).data for _ in range(count)]
        return books

    return _create_books
