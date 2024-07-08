import asyncio

from aiogram import types, Dispatcher
from aiogram.filters import CommandStart, Command
from bot import keyboards, config, filters
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, ReplyKeyboardBuilder, KeyboardButton
import tools
from sqlalchemy import select
from bot import models
from datetime import datetime
from aiogram import F
from bot.services.haversine_formula import get_nearest_location
import requests
import re


async def start_handler(message: types.Message):
    # await message.delete()
    user_location = {
        'lat': message.location.latitude,
        'lon': message.location.longitude
    }

    r = requests.get("https://api.yclients.com/api/v1/companies?my=1&showBookforms=1&count=100", headers=config.YCLIENTS_HEADERS)
    salons: list = r.json()["data"]
    print(salons[0])

    nearest_salon: list = get_nearest_location(salons, user_location)
    keyboard = InlineKeyboardBuilder()
    for salon in nearest_salon:

        btn = InlineKeyboardButton(
            text=f"{salon['title']} >",
            callback_data=f"near_salon_{salon['id']}"
        )
        keyboard.row(btn)

    btn = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="back_to_main"
    )
    keyboard.row(btn)

    await message.answer(
        text="Ближайшие салоны:",
        reply_markup=keyboard.as_markup()
    )

    # keyboard = types.ReplyKeyboardRemove()
    # x = await message.answer(
    #     text="44",
    #     reply_markup=keyboard
    # )
    # await x.delete()


async def select_salon_handler(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()

    r = requests.get("https://api.yclients.com/api/v1/companies?my=1&showBookforms=1&count=100", headers=config.YCLIENTS_HEADERS)
    salons: list = r.json()["data"]
    salon_id = re.findall(r"near_salon_(.+)", callback.data)[0]

    salon = [s for s in salons if s["id"] == int(salon_id)][0]

    kb = [
        [
            types.KeyboardButton(text="◀️ Назад"),
        ]
    ]

    keyboard = types.ReplyKeyboardRemove()

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

    await callback.message.answer_venue(
        title=salon["title"],
        address=salon["address"],
        latitude=salon["coordinate_lat"],
        longitude=salon["coordinate_lon"],
        reply_markup=keyboard.as_markup()
    )


def setup(dp: Dispatcher):
    dp.message.register(start_handler, F.content_type == types.ContentType.LOCATION)
    dp.callback_query.register(select_salon_handler, F.data.regexp(r"near_salon_(.+)"))


