import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "/app/books_test.db")

def get_stock(book_id: int) -> int:
    conn = sqlite3.connect(DB_PATH, timeout=10)
    row = conn.execute("SELECT stock FROM books WHERE id = ?", (book_id,)).fetchone()
    conn.close()
    return row[0] if row else 0

def reserve_stock(book_id: int, quantity: int) -> bool:
    conn = sqlite3.connect(DB_PATH, timeout=10)
    row = conn.execute("SELECT stock FROM books WHERE id = ?", (book_id,)).fetchone()
    if not row or row[0] < quantity:
        conn.close()
        return False
    conn.execute("UPDATE books SET stock = stock - ? WHERE id = ?", (quantity, book_id))
    conn.commit()
    conn.close()
    return True

def release_stock(book_id: int, quantity: int) -> bool:
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.execute("UPDATE books SET stock = stock + ? WHERE id = ?", (quantity, book_id))
    conn.commit()
    conn.close()
    return True
