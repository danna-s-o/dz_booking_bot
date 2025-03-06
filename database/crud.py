# booking_bot/database/crud.py

import sqlite3

def execute_query(query: str, params: dict = None):
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        return result
    except sqlite3.Error as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return None
    finally:
        conn.close()


# Заполнение таблицы столиков
def add_tables_data():
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()

    # Список столиков: (местоположение, вместимость, количество)
    tables_data = [
        ('у окна', 4, 3),
        ('в зале', 6, 8)
    ]

    for location, capacity, count in tables_data:
        for _ in range(count):
            cursor.execute('''
                INSERT INTO tables (location, capacity)
                VALUES (?, ?)
            ''', (location, capacity))

    conn.commit()
    conn.close()


# Проверка на существование таблицы со столиками
def is_tables_empty() -> bool:
    query = "SELECT COUNT(*) FROM tables;"
    result = execute_query(query)
    return result and result[0][0] == 0


# Получение доступных столиков на определенную дату и время
def get_available_tables(date: str, time: str) -> list:
    query = """
        SELECT t.location, t.capacity, COUNT(t.id) AS available_count
        FROM tables t
        WHERE NOT EXISTS (
            SELECT 1
            FROM reservations r
            WHERE r.table_id = t.id
              AND r.date = :date
              AND (
              (r.time BETWEEN TIME(:time, '-0 minutes') AND TIME(:time, '+89 minutes'))
              OR
              (:time BETWEEN TIME(r.time, '-0 minutes') AND TIME(r.time, '+89 minutes'))
              )
        )
        GROUP BY t.location, t.capacity;
    """
    return execute_query(query, {"date": date, "time": time})


# Проверка доступности конкретного столика к бронированию при подтверждении брони
def is_table_available(date: str, time: str, guests: int, location: str) -> bool:
    query = """
        SELECT COUNT(t.id) AS available_count
        FROM tables t
        WHERE t.capacity >= :guests
          AND (:location = 'не имеет значения' OR t.location = :location)
          AND NOT EXISTS (
              SELECT 1
              FROM reservations r
              WHERE r.table_id = t.id
                AND r.date = :date
                AND (
                (r.time BETWEEN TIME(:time, '-0 minutes') AND TIME(:time, '+89 minutes'))
                OR
                (:time BETWEEN TIME(r.time, '-0 minutes') AND TIME(r.time, '+89 minutes'))
                ) 
          );
    """
    result = execute_query(query, {"date": date, "time": time, "guests": guests, "location": location})

    if result and result[0][0] > 0:
        return True
    return False


# Выбор первого доступного подходящего под запрос столика для занесения в базу данных
def find_available_table(date: str, time: str, guests: int, location: str) -> int:
    query = """
        SELECT t.id
        FROM tables t
        WHERE t.capacity >= :guests
          AND (:location = 'не имеет значения' OR t.location = :location)
          AND NOT EXISTS (
              SELECT 1
              FROM reservations r
              WHERE r.table_id = t.id
                AND r.date = :date
                AND (
                (r.time BETWEEN TIME(:time, '-0 minutes') AND TIME(:time, '+89 minutes'))
                OR
                (:time BETWEEN TIME(r.time, '-0 minutes') AND TIME(r.time, '+89 minutes'))
                ) 
          )
        LIMIT 1;
    """
    result = execute_query(query, {"date": date, "time": time, "guests": guests, "location": location})
    return result[0][0] if result else None


# Добавление бронирования в базу данных
def insert_to_restaurant_table(telegram_id, name, surname, date, time, guests, preferences):

    table_id = find_available_table(date, time, guests, preferences)
    if not table_id:
        print("Нет доступных столиков для бронирования.")
        return False

    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    try:
        # Добавляем бронирование
        cursor.execute('''
            INSERT INTO reservations (table_id, telegram_id, name, surname, date, time, guests, preferences)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (table_id, telegram_id, name, surname, date, time, guests, preferences))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Ошибка при добавлении бронирования: {e}")
        return False
    finally:
        conn.close()


# Получение пользовательских броней
def get_user_bookings(telegram_id: int) -> list:
    query = """
    SELECT r.id, r.table_id, r.date, r.time, r.guests, r.preferences, r.name, r.surname  
    FROM reservations r
    WHERE r.telegram_id = :telegram_id
    """
    return execute_query(query, {"telegram_id": telegram_id})


# Удаление пользовательских броней
def delete_reservation(reservation_id: int, telegram_id: int) -> bool:
    query = """
    DELETE FROM reservations
    WHERE id = :reservation_id AND telegram_id = :telegram_id
    """
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    try:
        cursor.execute(query, {"reservation_id": reservation_id, "telegram_id": telegram_id})
        rows_deleted = cursor.rowcount
        conn.commit()
        return rows_deleted > 0
    except sqlite3.Error as e:
        print(f"Ошибка при удалении бронирования: {e}")
        return False
    finally:
        conn.close()



                           
