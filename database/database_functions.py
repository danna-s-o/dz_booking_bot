# booking_bot/database/database_functions.py

from aiogram.fsm.context import FSMContext

from booking_bot.database.crud import insert_to_restaurant_table, get_available_tables
import logging


async def cmd_filling_database(state: FSMContext):
    try:
        # Получаем данные из состояния
        user_data = await state.get_data()
        logging.info(f"Данные из состояния: {user_data}")

        # Проверяем наличие необходимых данных
        required_keys = ['date', 'time', 'guests', 'name', 'surname', 'telegram_id']
        if not all(key in user_data for key in required_keys):
            logging.error("Недостаточно данных для сохранения в базу данных")
            return

        # Сохраняем данные в базу данных
        insert_to_restaurant_table(
            user_data['telegram_id'],
            user_data['name'],
            user_data['surname'],
            user_data['date'],
            user_data['time'],
            user_data['guests'],
            user_data.get('preferences', 'не указано')  # preferences может быть необязательным
        )

        # Логируем успешное сохранение
        logging.info("Данные успешно сохранены в базу данных")

    except Exception as e:
        # Логируем ошибку
        logging.error(f"Ошибка при сохранении данных в базу данных: {e}")


