from aiogram import types, Dispatcher
from aiogram.filters import CommandStart, Command
from bot import keyboards, config, filters
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, ReplyKeyboardBuilder, KeyboardButton
import tools
from sqlalchemy import select
from bot import models
from datetime import datetime


async def start_handler(message: types.Message):
    kb = [
        [
            types.KeyboardButton(text="Записаться"),
            types.KeyboardButton(text="Мои записи")
         ]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(
        text="Welcome dear user! This is our bot.",
        reply_markup=keyboard
    )





def setup(dp: Dispatcher):
    dp.message.register(start_handler, CommandStart())
