from aiogram import types, Dispatcher
from aiogram.filters import CommandStart, Command
from bot import keyboards, config, filters
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, ReplyKeyboardBuilder, KeyboardButton
import tools
from sqlalchemy import select
from bot import models
from datetime import datetime
from aiogram import F


async def start_handler(message: types.Message):
    kb = [
        [
            types.KeyboardButton(text="Поиск 🔎"),
            types.KeyboardButton(text="Ближайший 📍", request_location=True),
        ],
        [
            types.KeyboardButton(text="◀️ Назад"),
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
    # btn = InlineKeyboardButton(
    #     text="◀️ Назад",
    #     callback_data="back_to_main"
    # )
    # keyboard.row(btn)
    await message.answer(
        text="Выберите",
        reply_markup=keyboard
    )


def setup(dp: Dispatcher):
    dp.message.register(start_handler, F.text == "Записаться")
