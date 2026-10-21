import json
from dataclasses import asdict

import requests
from typing import Any, Dict
from src.models.response_models import BookResponse, ApiResponse, BookListResponse, AuthorListResponse, AuthorResponse, \
    GeneralErrorResponse, UserResponse, OrderResponse, InventoryResponse


class HTTPClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        return self.session.request(method, url, **kwargs)

    def get_books(self) -> ApiResponse:
        response = self._request("GET", "books")
        data = response.json()
        return ApiResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            data=BookListResponse(books=[BookResponse(**item) for item in data])
        )

    def get_book(self, book_id: int) -> ApiResponse:
        response = self._request("GET", f"books/{book_id}")

        if response.status_code != 200:
            return ApiResponse(
                status_code=response.status_code,
                headers=dict(response.headers),
                data=GeneralErrorResponse(**response.json()) if response.text else None
            )

        return ApiResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            data=BookResponse(**response.json())
        )

    def post_book(self, data: Dict[str, Any]) -> ApiResponse:
        response = self._request("POST", "books", json=data)

        if response.status_code != 201:
            return ApiResponse(
                status_code=response.status_code,
                headers=dict(response.headers),
                data=GeneralErrorResponse(**response.json()) if response.text else None
            )

        return ApiResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            data=BookResponse(**response.json())
        )

    def post_inventory(self, data: Dict[str, Any]) -> ApiResponse:
        response = self._request("POST", "inventory", json=data)
        if response.status_code != 200:
            return ApiResponse(
                status_code=response.status_code,
                headers=dict(response.headers),
                data=GeneralErrorResponse(**response.json()) if response.text else None
            )
        return ApiResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            data=response.json()
        )

    def get_inventory(self, book_id: int) -> ApiResponse:
        response = self._request("GET", f"inventory/{book_id}")
        if response.status_code != 200:
            return ApiResponse(
                status_code=response.status_code,
                headers=dict(response.headers),
                data=GeneralErrorResponse(**response.json()) if response.text else None
            )
        return ApiResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            data=InventoryResponse(**response.json())
        )

    def post_order(self, data: Dict[str, Any]) -> ApiResponse:
        response = self._request("POST", "orders", json=data)

        if response.status_code != 201:
            return ApiResponse(
                status_code=response.status_code,
                headers=dict(response.headers),
                data=GeneralErrorResponse(**response.json()) if response.text else None
            )

        return ApiResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            data=OrderResponse(**response.json())
        )

    def patch_book(self, book_id: int, data: Dict[str, Any]) -> ApiResponse:
        response = self._request("PATCH", f"books/{book_id}", json=data)

        if response.status_code != 200:
            return ApiResponse(
                status_code=response.status_code,
                headers=dict(response.headers),
                data=GeneralErrorResponse(**response.json()) if response.text else None
            )

        return ApiResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            data=BookResponse(**response.json())
        )


    def put_book(self, book_id: int, data: Dict[str, Any]) -> ApiResponse:
        response = self._request("PUT", f"books/{book_id}", json=data)

        if response.status_code != 200:
            return ApiResponse(
                status_code=response.status_code,
                headers=dict(response.headers),
                data=GeneralErrorResponse(**response.json()) if response.text else None
            )

        return ApiResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            data=BookResponse(**response.json())
        )


    def delete_book(self, book_id: int) -> ApiResponse:
        response = self._request("DELETE", f"books/{book_id}")

        if response.status_code != 204:
            return ApiResponse(
                status_code=response.status_code,
                headers=dict(response.headers),
                data=GeneralErrorResponse(**response.json()) if response.text else None
            )

        return ApiResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            data=None
        )


    def get_authors(self) -> ApiResponse:
        response = self._request("GET", "authors")

        if response.status_code != 200:
            return ApiResponse(
                status_code=response.status_code,
                headers=dict(response.headers),
                data=GeneralErrorResponse(**response.json()) if response.text else None
            )

        data = response.json()
        return ApiResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            data=AuthorListResponse(authors=[AuthorResponse(**item) for item in data])
        )

    def get_author(self, author_id: int) -> ApiResponse:
        response = self._request("GET", f"authors/{author_id}")

        if response.status_code != 200:
            return ApiResponse(
                status_code=response.status_code,
                headers=dict(response.headers),
                data=GeneralErrorResponse(**response.json()) if response.text else None
            )

        return ApiResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            data=AuthorResponse(**response.json())
        )

    def delete_author(self, author_id: int) -> ApiResponse:
        response = self._request("DELETE", f"authors/{author_id}")

        if response.status_code != 204:
            return ApiResponse(
                status_code=response.status_code,
                headers=dict(response.headers),
                data=GeneralErrorResponse(**response.json()) if response.text else None
            )

        return ApiResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            data=None
        )

    def register_user(self, payload) -> ApiResponse:
        response = self._request("POST", "register", json=asdict(payload))
        return ApiResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            data=UserResponse(**response.json()) if response.text else None
        )

    def login(self, username: str, password: str) -> ApiResponse:
        payload = {
            "username": username,
            "password": password
        }
        response = self._request("POST", "login", json=payload)
        return ApiResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            data=response.json() if response.text else None
        )

    def logout(self) -> ApiResponse:
        response = self._request("POST", "logout")
        return ApiResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            data=response.json() if response.text else None
        )

    def clear_inventory(self) -> ApiResponse:
        response = self._request("DELETE", "inventory")
        return ApiResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            data=response.json() if response.text else None
        )
