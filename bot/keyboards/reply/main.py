from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, ReplyKeyboardBuilder, KeyboardButton
from aiogram import types


kb = [
    [
        types.KeyboardButton(text="Записаться"),
        types.KeyboardButton(text="Мои записи")
    ],
]
keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)