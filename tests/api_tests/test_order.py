import allure
import pytest_check as check
from conftest import BookFactory


@allure.epic("Bookstore API")
@allure.story("Create Order")
class TestCreateOrder:
    @allure.title("Sending POST request and getting 201 response")
    def test_create_order_success(self, api_client):
        with allure.step("Prepare data: create a book"):
            payload = BookFactory.create_payload()
            book_response = api_client.post_book(data=payload)
            book_id = book_response.data.id

        with allure.step("Add stock for the book"):
            inventory_payload = {"book_id": book_id, "quantity": 10}
            inventory_response = api_client.post_inventory(data=inventory_payload)
            check.equal(inventory_response.status_code, 200)

        with allure.step("Check initial stock is 10"):
            stock_before = api_client.get_inventory(book_id)
            check.equal(stock_before.data.quantity, 10)

        with allure.step("Create Order"):
            order_payload = {"book_id": book_id, "quantity": 2}
            response = api_client.post_order(data=order_payload)

        with allure.step("Checking order response with 201"):
            check.equal(response.status_code, 201)
            check.equal(response.data.book_id, book_id)
            check.equal(response.data.quantity, 2)
            check.equal(response.data.status, "pending")
            check.is_not_none(response.data.id)

        with allure.step("Check stock decreased to 8"):
            stock_after = api_client.get_inventory(book_id)
            check.equal(stock_after.data.quantity, 8)