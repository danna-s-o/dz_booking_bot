# booking_bot/handlers/booking.py

import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from utils.texts import *
from keyboards.inline_keyboards import *
from state.state import *
from handlers.is_valid import *
from dicts.preferences import *
from database.crud import *
from handlers.payment import cmd_send_invoice

router = Router()


# Обработчик команды /start
@router.message(Command('start'))
async def cmd_start(message: Message):
    await message.answer(start_text)

# Обработчик команды /menu
@router.message(Command('menu'))
async def cmd_start(message: Message):
    await message.answer(menu_text)


# Обработчик команды /available
@router.message(Command('available'))
async def cmd_check_date(message: Message, state: FSMContext):
    await message.answer("📅 Введите интересующую вас дату в формате дд.мм.гг\n"
                         "<code>Например: 31.12.25</code>",
                                           parse_mode=ParseMode.HTML)
    await state.set_state(CheckingDateProcess.set_date)


# Обработчик ввода интересующей даты
@router.message(CheckingDateProcess.set_date)
async def cmd_set_date(message: Message, state: FSMContext):
    checking_date = message.text

    if is_valid_date(checking_date):
        await state.update_data(date=message.text)
        await message.answer("🕙 Введите время в формате ЧЧ:MM\n"
                             "<code>Например: 14:30</code>",
                                               parse_mode=ParseMode.HTML)
        await state.set_state(CheckingDateProcess.set_time)
    else:
        await message.answer('❌ Дата не распознана или уже прошла. '
                             'Пожалуйста, введите дату в формате дд.мм.гг\n'
                             "<code>Например: 31.12.25</code>",
                             parse_mode=ParseMode.HTML
                             )
        await state.set_state(CheckingDateProcess.set_date)


# Обработчик ввода интересующих часов
@router.message(CheckingDateProcess.set_time)
async def cmd_set_time(message: Message, state: FSMContext):
    checking_time = message.text
    user_data = await state.get_data()

    if is_valid_time(checking_time, user_data['date']):
        if is_working_hours(checking_time, user_data['date']):
            await state.update_data(time=message.text)
            user_data = await state.get_data()
            available_tables = get_available_tables(user_data['date'], user_data['time'])
            if available_tables:
                response = "<b>Доступные столики</b>:\n\n"
                for location, capacity, count in available_tables:
                    response += (
                        f"Расположение: {location}\n"
                        f"👥 Посадочных мест: {capacity}\n"
                        f"✔️ Свободно: {count}\n\n"
                    )
                response += "Если хотите приступить к бронированию, нажмите /book\n\n☰ /menu"
                await message.answer(response, parse_mode=ParseMode.HTML)
            else:
                await message.answer("❌ На выбранные дату и время свободных столиков нет.\n"
                                     "Попробуйте выбрать другое время или дату.\n\n☰ /menu")

            await state.clear()
        else:
            await message.answer(not_working_time_text)
            await state.set_state(CheckingDateProcess.set_time)


# Обработчик команды /book
@router.message(Command('book'))
async def cmd_book(message: Message):
    await message.answer('Вы хотите забронировать столик?', reply_markup=ready_or_not_kb())


# Обработчик callback-запроса "ready"
@router.callback_query(F.data == 'ready')
async def cmd_ready(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.edit_text("📅 Введите дату в формате дд.мм.гг\n"
                                           "<code>Например: 31.12.25</code>",
                                           parse_mode=ParseMode.HTML
                                           )
    await state.set_state(BookingProcces.choosing_date)

# Обработчик callback-запроса "not_ready"
@router.callback_query(F.data == 'not_ready')
async def cmd_not_ready(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.edit_text("Хорошо. Как только вы будете готовы к бронированию столика, "
                                           "можете обратиться ко мне по команде /book\n\n☰ /menu")


# Обработчик ввода даты
@router.message(BookingProcces.choosing_date)
async def cmd_choosing_date(message: Message, state: FSMContext):
    user_date = message.text

    if is_valid_date(user_date):
        await state.update_data(date=user_date)
        await message.answer(f"Вы выбрали дату: {user_date} "
                             f"\n🕙 Теперь введите время в формате ЧЧ:ММ\n"
                             "<code>Например: 13:40</code>",
                             parse_mode=ParseMode.HTML
                             )

        await state.set_state(BookingProcces.choosing_time)
    else:
        await message.answer('❌ Дата не распознана или уже прошла. '
                             'Пожалуйста, введите дату в формате дд.мм.гг\n'
                             "<code>Например: 31.12.25</code>",
                             parse_mode=ParseMode.HTML
                             )
        await state.set_state(BookingProcces.choosing_date)


# Обработчик ввода времени
@router.message(BookingProcces.choosing_time)
async def cmd_choosing_time(message: Message, state: FSMContext):
    user_time = message.text
    user_date = await state.get_data()

    if is_valid_time(user_time, user_date['date']):
        if is_working_hours(user_time, user_date['date']):

            await state.update_data(time=message.text)
            await message.answer(f"Вы выбрали время: {user_time}\n"
                                 f"👥 Теперь введите количество гостей.\n"
                                 "<code>Например: 4</code>",
                                 parse_mode=ParseMode.HTML
                                 )
            await state.set_state(BookingProcces.set_quantity_of_guests)

        else:
            await message.answer(not_working_time_text)
            await state.set_state(BookingProcces.choosing_time)

    else:
        await message.answer('❌ Время не распознано или уже прошло. '
                             'Пожалуйста, введите время в формате ЧЧ:ММ\n'
                             "<code>Например: 13:40</code>",
                             parse_mode=ParseMode.HTML
                             )
        await state.set_state(BookingProcces.choosing_time)


# Обработчик ввода количества гостей
@router.message(BookingProcces.set_quantity_of_guests)
async def cmd_set_quantity_of_guests(message: Message, state: FSMContext):
    try:
        user_guests = int(message.text)

        if 0 < user_guests <= 6:
            await state.update_data(guests=user_guests)
            await message.answer(f"Количество гостей: {message.text}\n"
                                 f"🗒️ Теперь укажите ваши пожелания.\n"
                                 f"Какой столик вы предпочитаете?", reply_markup=preferences_kb())
            await state.set_state(BookingProcces.set_preferences)

        elif user_guests > 6:
            await message.answer('К сожалению, в нашем ресторане нет столиков для такого '
                                 'количества гостей. Вы можете начать бронирование '
                                 'с другими параметрами по команде /book')
            await state.clear()

        else:
            await message.answer('❌ Количество гостей должно быть положительным числом. '
                                'Пожалуйста, введите число больше 0\n'
                                 '<code>Например: 4</code>',
                                 parse_mode=ParseMode.HTML
                                 )
            await state.set_state(BookingProcces.set_quantity_of_guests)

    except ValueError:
        await message.answer('❌ Не удалось распознать число гостей. Убедитесь, что ввели именно число.\n'
                             '<code>Например: 4</code>',
                             parse_mode=ParseMode.HTML
                             )
        await state.set_state(BookingProcces.set_quantity_of_guests)


# Обработчик callback-запроса предпочтений
@router.callback_query(BookingProcces.set_preferences, F.data.in_(preferences_dict))
async def cmd_set_preferences(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    user_preferences = preferences_dict[callback_query.data].lower()
    await state.update_data(preferences=user_preferences)
    user_data = await state.get_data()

    if user_preferences == 'у окна' and user_data['guests'] > 4:
        await callback_query.message.answer(f'К сожалению, у столиков у окна нет {user_data['guests']} '
                                            f'посадочных мест, но мы можем предложить вам изменить выбор '
                                            f'в пользу столика в зале')
    else:

        if is_table_available(user_data['date'], user_data['time'], user_data['guests'], user_data['preferences']):

            text = (f"<b>Детали бронирования:</b>\n"
                f"• Место столика: {user_data['preferences']}\n"
                f"• Гости: {user_data['guests']}\n"
                f"• Дата: {user_data['date']}\n"
                f"• Время: {user_data['time']}\n\n"
                f"Вы подтверждаете эти данные?")

            await callback_query.message.answer(f"{text}", parse_mode=ParseMode.HTML,
                                                   reply_markup=confirm_kb())
            await state.set_state(BookingProcces.confirm_booking)
        else:
            await callback_query.message.answer('🚫 К сожалению, свободного столика по вашему запросу нет.\n'
                                                'Вы можете проверить доступные для брони столики по команде /available\n\n'
                                                '☰ /menu')
            await state.clear()


# Обработчик подтверждения брони
@router.callback_query(BookingProcces.confirm_booking, F.data == 'yes')
async def cmd_confirm_booking(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.answer('👤 Укажите, на чье имя оформляется бронь в формате: Имя Фамилия')
    await state.set_state(BookingProcces.get_name_surname)


# Обработчик ввода имени и фамилии
@router.message(BookingProcces.get_name_surname)
async def cmd_get_name_surname(message: Message, state: FSMContext):
    try:
        user_name, user_surname = map(str, message.text.split(' '))
        await state.update_data(name=user_name, surname=user_surname, telegram_id=message.chat.id)

        await state.set_state(None)

        await message.answer('💳 Для закрепления брони необходимо ее оплатить. '
                             'Обращаем ваше внимание, что эта операция возможна только в мобильной версии',
                             reply_markup=proceed_to_payment_kb())

    except ValueError:
        await message.answer('❌ Пожалуйста, укажите имя и фамилию в одном сообщении через пробел')
        await state.set_state(BookingProcces.get_name_surname)


# Обработчик оплаты брони
@router.callback_query(F.data == 'proceed_to_payment')
async def cmd_waiting_for_payment(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    message = callback_query.message

    # Вызов функции отправки счета
    try:
        await cmd_send_invoice(message, state)
    except Exception as e:
        logging.error(f"Ошибка при отправке счета: {e}")
        await message.answer("❌ Произошла ошибка при отправке счета. "
                             "Пожалуйста, попробуйте позже\n\n☰ /menu")


# Обработчик отмены брони
@router.callback_query(BookingProcces.confirm_booking, F.data == 'no')
async def cmd_cancel_booking(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.edit_text("Бронирование отменено. Ваши данные не были сохранены. "
                                           "Как только вы будете готовы, "
                                           "можете снова обратиться по команде /book\n\n☰ /menu")
    await state.clear()


@router.message(Command('my_bookings'))
async def cmd_my_bookings(message: Message):
    telegram_id = message.from_user.id
    bookings = get_user_bookings(telegram_id)

    if not bookings:
        await message.answer("У вас нет активных бронирований.\n"
                             "Если хотите зарезервировать столик, нажмите /book\n\n☰ /menu")
        return

    response = "<b>Ваши бронирования:</b>\n\n"
    for booking in bookings:
        response += (
            f"🆔 номер брони: {booking[0]}\n"
            f"🆔 номер столика: {booking[1]}\n"
            f"Дата: {booking[2]}\n"
            f"Время: {booking[3]}\n"
            f"Гости: {booking[4]}\n"
            f"Место столика {booking[5]}\n"
            f"На имя: {booking[6]} {booking[7]}\n\n"
        )

    await message.answer(response, parse_mode=ParseMode.HTML)


@router.message(Command('cancel'))
async def cmd_cancel(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    bookings = get_user_bookings(telegram_id)

    if not bookings:
        await message.answer("У вас нет активных бронирований")
        return

    response = "<b>Ваши бронирования:</b>\n\n"
    for booking in bookings:
        response += (
            f"🆔 номер брони: {booking[0]}\n"
            f"🆔 номер столика: {booking[1]}\n"
            f"Дата: {booking[2]}\n"
            f"Время: {booking[3]}\n"
            f"Гости: {booking[4]}\n"
            f"Место столика {booking[5]}\n"
            f"На имя: {booking[6]} {booking[7]}\n\n"
        )

    await message.answer(response, parse_mode=ParseMode.HTML)
    await message.answer('Пришлите id номер брони, которую вы хотите отменить')
    await state.set_state(CancellingProccess.choosing_id)

@router.message(CancellingProccess.choosing_id)
async def cmd_choosing_id(message: Message, state: FSMContext):
    try:
        reservation_id = int(message.text)
        telegram_id = message.chat.id

        if delete_reservation(reservation_id, telegram_id):
            await message.answer(f'✅ Бронь №{reservation_id} успешно отменена.')
            await message.answer(
                'Для просмотра ваших текущих броней нажмите /my_bookings\n'
                'Для нового бронирования нажмите /book\n\n☰ /menu'
            )
            await state.clear()
        else:
            await message.answer(
                '❌ Бронь не найдена или не принадлежит вам.\n'
                'Пожалуйста, проверьте id и попробуйте снова по команде /cancel\n\n☰ /menu'
            )
            await state.clear()

    except ValueError:
        await message.answer(
            '❌ Некорректный ID бронирования. Пожалуйста, введите число.\n'
            'Например: 123\n'
            'Попробуйте снова по команде /cancel\n\n☰ /menu'
        )
        await state.clear()

    except Exception as e:
        logging.error(f"Ошибка в обработчике cmd_choosing_id: {e}", exc_info=True)
        await message.answer(
            '❌ Произошла ошибка при отмене бронирования. Пожалуйста, попробуйте позже\n\n☰ /menu'
        )
        await state.clear()

@router.message(F.text)
async def cmd_text(message: Message):
    await message.answer('Для взаимодействия обратитесь по одной из доступных команд в /menu')



