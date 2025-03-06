# booking_bot/keyboards/inline_keyboards.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from booking_bot.dicts.preferences import *


def ready_or_not_kb():
    kb = [
        [InlineKeyboardButton(text='Да', callback_data='ready')],
        [InlineKeyboardButton(text='Нет', callback_data='not_ready')]
    ]
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    return inline_keyboard


def preferences_kb():
    kb = [
        [InlineKeyboardButton(text=text, callback_data=callback_data)]
        for callback_data, text in preferences_dict.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def confirm_kb():
    kb = [
        [InlineKeyboardButton(text='Да', callback_data='yes')],
        [InlineKeyboardButton(text='Нет', callback_data='no')]
    ]
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    return inline_keyboard


def proceed_to_payment_kb():
    kb = [
        [InlineKeyboardButton(text='Перейти к оплате', callback_data='proceed_to_payment')]
    ]
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    return inline_keyboard
