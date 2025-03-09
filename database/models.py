import sqlite3

def createRestaurantDatabase():
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()

    # Таблица со столиками
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tables(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location VARCHAR(50) NOT NULL,
        capacity INTEGER NOT NULL
    )''')

    # Таблица с бронями
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reservations(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_id INTEGER,
        telegram_id INTEGER,
        name TEXT, 
        surname TEXT,
        date TEXT,
        time TEXT,
        guests INTEGER,
        preferences TEXT,
        FOREIGN KEY (table_id) REFERENCES tables(id)
    )''')


    conn.commit()
    conn.close()