from aiogram import Bot, Dispatcher
from utils.config import TOKEN
import asyncio
import logging
from handlers.booking import router as booking_router
from handlers.payment import router as payment_router
from database.models import init_db
from database.crud import is_tables_empty, add_tables_data



async def main():
    logging.basicConfig(level=logging.INFO)
    init_db()

    if is_tables_empty():
        add_tables_data()
    else:
        logging.info("Таблица столиков уже содержит данные. Пропускаем заполнение.")

    bot = Bot(TOKEN)
    dp = Dispatcher()

    dp.include_routers(booking_router, payment_router)

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())