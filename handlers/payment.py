# booking_bot/handlers/payment.py

import logging

from aiogram.types import Message, LabeledPrice, PreCheckoutQuery
from aiogram.fsm.context import FSMContext
from aiogram import Router, F

from utils.config import PAYMENT_TOKEN
from database.database_functions import cmd_filling_database

router = Router()


PRICE = [LabeledPrice(label="Бронирование столика", amount=1000 * 100)]

async def cmd_send_invoice(message: Message, state: FSMContext):
    try:
        user_data = await state.get_data()

        date = user_data['date']
        time = user_data['time']
        guests = user_data['guests']

        # Оописание
        if guests == 1:
            var_text = f"Бронирование столика в ресторане на {date} в {time} для {guests} гостя. "
        else:
            var_text = f"Бронирование столика в ресторане на {date} в {time} для {guests} гостей. "

        description = (
            f"{var_text} "
            f"Пожалуйста, проверьте данные перед оплатой"
        )


        # Счет
        await message.answer_invoice(
            title='Бронирование столика',
            description=description,
            payload='reservation-access',
            provider_token=PAYMENT_TOKEN,
            currency='RUB',
            prices=PRICE
        )

        # Логируем успешную отправку счета
        logging.info("Счет успешно отправлен")

    except Exception as e:
        # Логируем ошибку
        logging.error(f"Ошибка в cmd_send_invoice: {e}")
        await message.answer("Произошла ошибка при отправке счета. Пожалуйста, попробуйте позже\n\n/menu")

@router.pre_checkout_query()
async def pre_checkout_query_handler(pre_checkout_query: PreCheckoutQuery):
    # Подтверждаем запрос на оплату
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment_handler(message: Message, state: FSMContext):

    await message.answer('Оплата прошла успешно! Ваше бронирование подтверждено\n\n/menu')

    # Сохраняем данные в базу данных
    await cmd_filling_database(state)

    # Очищаем все состояния
    await state.clear()

