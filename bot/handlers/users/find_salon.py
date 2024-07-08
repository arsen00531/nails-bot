from aiogram import types, Dispatcher
from aiogram.filters import CommandStart, Command
from bot import keyboards, config, filters
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, ReplyKeyboardBuilder, KeyboardButton
import tools
from sqlalchemy import select
from bot import models
from datetime import datetime
from aiogram import F
from aiogram.fsm.context import FSMContext
from bot.states import FindSalonStates
import requests
import re


async def start_handler(message: types.Message, state: FSMContext):
    keyboard = InlineKeyboardBuilder()
    btn = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="back_to_main"
    )
    keyboard.row(btn)

    await message.answer(
        text="Напишите название метро (Менделеевская, Сухаревская)"
             " или название улицы (Новослободская, Тверская-Ямская)",
        keyboard=keyboard.as_markup()
    )
    await state.set_state(FindSalonStates.get_data)


async def get_data_handler(message: types.Message, state: FSMContext):
    await state.clear()
    r = requests.get(
        "https://api.yclients.com/api/v1/companies?id=1042269&showBookforms=1",
        headers=config.YCLIENTS_HEADERS
    )

    salons: list = r.json()["data"]

    match_title = [i for i in salons if re.findall(message.text, i["title"], flags=re.I)]
    match_address = [i for i in salons if re.findall(message.text, i["address"], flags=re.I)]

    if match_title:
        salon = match_title[0]
    elif match_address:
        salon = match_address[0]
    else:
        return await message.answer(
            text="Не нашли такой салон."
        )

    web_app_info = types.WebAppInfo(url=salon["bookforms"][0]["url"])
    keyboard = InlineKeyboardBuilder()
    btn = InlineKeyboardButton(
        text="Записаться",
        web_app=web_app_info
    )
    keyboard.row(btn)
    btn = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="back_to_main"
    )
    keyboard.row(btn)

    await message.answer(
        text=salon["title"],
        reply_markup=keyboard.as_markup()
    )




def setup(dp: Dispatcher):
    dp.message.register(start_handler, F.text == "Поиск 🔎")
    dp.message.register(get_data_handler, FindSalonStates.get_data)
