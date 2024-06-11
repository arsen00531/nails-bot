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
    print(message.location)
    keyboard = ReplyKeyboardBuilder()
    btn_1 = KeyboardButton(
        text="Найти"
    )
    btn_2 = KeyboardButton(
        text="Ближайший",
        request_location=True
    )
    keyboard.row(btn_1, btn_2)
    await message.answer(
        text="Выберите салон:",
        reply_markup=keyboard.as_markup(resize_markup=True, one_time_keyboard=True)
    )


def setup(dp: Dispatcher):
    dp.message.register(start_handler, F.content_type == types.ContentType.LOCATION)
