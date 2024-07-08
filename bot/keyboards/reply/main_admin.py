from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, ReplyKeyboardBuilder, KeyboardButton
from aiogram import types


kb = [
    [
        types.KeyboardButton(text="Записаться"),
        types.KeyboardButton(text="Мои записи")
    ],
    [
        types.KeyboardButton(text="Админ панель"),
    ],
]
keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)