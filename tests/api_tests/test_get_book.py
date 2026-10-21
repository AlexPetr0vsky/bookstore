import time
from random import randint
import allure
import pytest_check as check

BOOKS_COUNT = 5


@allure.epic("Bookstore API")
@allure.story("Get book")
class TestGetBooks:


    @allure.title("Sending GET request to get list of books, getting 200 response")
    def test_get_books_1(self, api_client, create_books):
        with allure.step("Create Book"):
            created_books = create_books(count=BOOKS_COUNT)

            time.sleep(600)

        with allure.step("Sending get books request"):
            response = api_client.get_books()

        with allure.step("Checking response with 200"):
            check.equal(response.status_code, 200)

            check.equal(len(response.data.books), len(created_books))
            for item in range(len(response.data.books)):
                check.equal(response.data.books[item].id, created_books[item].id)
                check.equal(response.data.books[item].book, created_books[item].book)
                check.equal(response.data.books[item].description, created_books[item].description)
                check.equal(response.data.books[item].author_id, created_books[item].author_id)
                check.equal(response.data.books[item].icon_book, created_books[item].icon_book)


@allure.epic("Bookstore API")
@allure.story("Get book")
class TestGetBook:
    @allure.title("Sending GET request to get a book by id, getting 200 response")
    @allure.epic("Bookstore API")
    def test_get_book_1(self, api_client, create_books):
        with allure.step("Create books"):
            books = create_books(count=BOOKS_COUNT)
            book = books[randint(1, BOOKS_COUNT) - 1]

        with allure.step("Sending get books request"):
            response = api_client.get_book(book_id=book.id)

        with allure.step("Checking response with 200"):
            check.equal(response.status_code, 200)
            check.equal(response.data.id, book.id)
            check.equal(response.data.book, book.book)
            check.equal(response.data.author_id, book.author_id)
            check.equal(response.data.icon_book, book.icon_book)
            check.equal(response.data.description, book.description)

    @allure.title("Sending GET request to get a book by wrong id, getting 404 response")
    @allure.epic("Bookstore API")
    def test_get_book_2(self, api_client, create_books):
        with allure.step("Create books"):
            created_books = create_books(count=BOOKS_COUNT)
            check.greater(len(created_books), 0)

        with allure.step("Sending get books request"):
            response = api_client.get_book(book_id=BOOKS_COUNT+1)

        with allure.step("Checking response with 404"):
            check.equal(response.status_code, 404)
            check.equal(response.data.error, "Book not found")
