import sqlite3
from contextlib import contextmanager

DATABASE_FILE = "restaurant.db"

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            phone_number TEXT
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            date TEXT,
            time TEXT,
            guests INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        conn.commit()