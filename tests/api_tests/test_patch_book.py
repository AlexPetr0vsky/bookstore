from random import randint

import allure
import pytest_check as check

BOOKS_COUNT = 5


@allure.epic("Bookstore API")
@allure.story("Patch book")
class TestPatchBook:
    @allure.title("Sending PATCH request to patch book by id, getting 200 response")
    def test_patch_book_1(self, api_client, create_books):
        with allure.step("Create books"):
            books = create_books(count=BOOKS_COUNT)
            book = books[randint(1, BOOKS_COUNT) - 1]

        with allure.step("Sending patch book request"):
            patch_payload = {"description": "Updated description"}
            response = api_client.patch_book(book_id=book.id, data=patch_payload)

        with allure.step("Checking response with 200"):
            check.equal(response.status_code, 200)
            check.equal(response.data.id, book.id)
            check.equal(response.data.book, book.book)
            check.equal(response.data.icon_book, book.icon_book)
            check.equal(response.data.description, patch_payload["description"])

    @allure.title("Sending PATCH request with wrong id, getting 404 response")
    def test_patch_book_2(self, api_client, create_books):
        with allure.step("Create books"):
            created_books = create_books(count=BOOKS_COUNT)
            check.greater(len(created_books), 0)

        with allure.step("Sending patch book request"):
            patch_payload = {"description": "Updated description"}
            response = api_client.patch_book(book_id=BOOKS_COUNT+1, data=patch_payload)

        with allure.step("Checking response with 404"):
            check.equal(response.status_code, 404)
            check.equal(response.data.error, "Book not found")
