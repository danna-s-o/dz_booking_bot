# booking_bot/handlers/is_valid.py

from datetime import datetime, time


# Функция для проверки корректности даты
def is_valid_date(date_str: str) -> bool:
    try:
        day, month, year = map(int, date_str.split('.'))

        input_datetime = datetime(year=2000 + year, month=month, day=day)
        current_datetime = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if input_datetime < current_datetime:
            return False
        return True
    except (ValueError, IndexError):
        return False


# Функция для проверки корректности времени
def is_valid_time(time_str: str, date_str: str) -> bool:
    try:
        hour, minute = map(int, time_str.split(':'))

        # Преобразуем введенную дату в объект datetime
        day, month, year = map(int, date_str.split('.'))
        input_datetime = datetime(year=2000 + year, month=month, day=day, hour=hour, minute=minute)

        # Получаем текущее время
        current_datetime = datetime.now()

        # Проверяем, что введенное время не меньше текущего (если дата сегодняшняя)
        if input_datetime.date() == current_datetime.date() and input_datetime < current_datetime:
            return False

        return True
    except (ValueError, IndexError):
        return False

# Функция для проверки соответствия времени рабочим часам
def is_working_hours(time_str: str, date_str: str) -> bool:
    try:
        hour, minute = map(int, time_str.split(':'))

        # Преобразуем введенную дату в объект datetime
        day, month, year = map(int, date_str.split('.'))
        input_datetime = datetime(year=2000 + year, month=month, day=day, hour=hour, minute=minute)

        # Получаем день недели (1 - понедельник, 7 - воскресенье)
        input_weekday = input_datetime.isoweekday()

        # Получаем введенные часы
        input_time = input_datetime.time()

        # Пределы рабочего дня (В ПН-ПТ с 10:00 до 22:00 и СБ-ВС с 10:00 до 23:00)
        start_working_time = time(hour=10, minute=0)  # Начало рабочего времени
        end_working_time_weekday = time(hour=22, minute=0)  # Конец рабочего времени в будни
        end_working_time_weekend = time(hour=23, minute=0)  # Конец рабочего времени в выходные

        # Проверяем, что время в пределах рабочего дня
        if input_weekday <= 5:  # Будни (ПН-ПТ)
            if start_working_time <= input_time < end_working_time_weekday:
                return True
        else:  # Выходные (СБ-ВС)
            if start_working_time <= input_time < end_working_time_weekend:
                return True

        # Если время не попадает в рабочие часы
        return False
    except (ValueError, IndexError):
        return False





