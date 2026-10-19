import sqlite3


DB_PATH = "inventory.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock (
            book_id INTEGER PRIMARY KEY,
            quantity INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def get_stock(book_id: int) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT quantity FROM stock WHERE book_id = ?", (book_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0


def reserve_stock(book_id: int, quantity: int) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT quantity FROM stock WHERE book_id = ?", (book_id,))
    row = cursor.fetchone()
    current = row[0] if row else 0

    if current < quantity:
        conn.close()
        return False

    if row:
        cursor.execute(
            "UPDATE stock SET quantity = quantity - ? WHERE book_id = ?",
            (quantity, book_id)
        )
    else:
        cursor.execute(
            "INSERT INTO stock (book_id, quantity) VALUES (?, ?)",
            (book_id, -quantity)
        )

    conn.commit()
    conn.close()
    return True


def release_stock(book_id: int, quantity: int) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT quantity FROM stock WHERE book_id = ?", (book_id,))
    row = cursor.fetchone()

    if row:
        cursor.execute(
            "UPDATE stock SET quantity = quantity + ? WHERE book_id = ?",
            (quantity, book_id)
        )
    else:
        cursor.execute(
            "INSERT INTO stock (book_id, quantity) VALUES (?, ?)",
            (book_id, quantity)
        )

    conn.commit()
    conn.close()
    return True