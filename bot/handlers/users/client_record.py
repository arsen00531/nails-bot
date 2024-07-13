import re

from aiogram import types, Dispatcher
from aiogram.filters import CommandStart, Command
from bot import keyboards, config, filters
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, ReplyKeyboardBuilder, KeyboardButton
import tools
from sqlalchemy import select
from bot import models
from datetime import datetime
from aiogram import F
import requests
import pytz
from bot.services.haversine_formula import get_nearest_location



async def start_handler(callback: types.CallbackQuery, session):
    await callback.answer()

    async with session() as open_session:
        user: models.sql.User = await open_session.execute(select(
            models.sql.User).filter_by(id=callback.from_user.id))
        user = user.scalars().first()

    datetime_now = datetime.now(pytz.timezone('Europe/Moscow'))
    datetime_now_month = datetime_now.month

    if datetime_now.month < 10:
        datetime_now_month = f"0{datetime_now.month}"

    datetime_now_day = datetime_now.day
    if datetime_now.day < 10:
        datetime_now_day = f"0{datetime_now.day}"

    response = requests.get(
        f"https://api.yclients.com/api/v1/records/{user.company_id}?page=1&count=500&start_date={datetime_now.year}-{datetime_now_month}-{datetime_now_day}",
        headers=config.YCLIENTS_HEADERS
    )
    records = []

    for record in response.json()["data"]:
        if not record.get("client"):
            continue
        if record.get("deleted"):
            continue
        if record.get("client")["phone"] == user.phone:
            records.append(record)

    records = records[:9]

    record_index = int(callback.data[:1])-1
    record = records[record_index]

    keyboard = InlineKeyboardBuilder()
    btn = InlineKeyboardButton(
        text="Связаться с администратором",
        callback_data="admin_support"
    )
    keyboard.row(btn)
    btn = InlineKeyboardButton(
        text="Отменить ❌",
        callback_data=f"delete_record_{record['id']}_{record['company_id']}"
    )
    keyboard.row(btn)
    btn = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="back_to_records"
    )
    keyboard.row(btn)
    text = ""

    datetime_object = datetime.strptime(record["datetime"], "%Y-%m-%dT%H:%M:%S%z")
    datetime_minute = datetime_object.minute
    if datetime_minute < 10:
        datetime_minute = f"0{datetime_minute}"

    r = requests.get(
        f"https://api.yclients.com/api/v1/companies?id={user.company_id}",
        headers=config.YCLIENTS_HEADERS
    )
    company = r.json()["data"][0]
    metro_station = re.findall(r"City\s+Nails\s+(.+)", company["title"])[0]

    record_titles = [s["title"] for s in record['services']]
    total_cost = sum([s["cost"] for s in record['services']])
    record_titles_string = " + ".join(record_titles)

    text += f"{callback.data} <b>{record_titles_string}</b>\n\n" \
            f"<b>Время</b>: <i>{datetime_object.day} {config.MONTHS[datetime_object.month]} в {datetime_object.hour}:{datetime_minute} МСК</i>" \
            f"\n" \
            f"<b>Мастер</b>: <i>{record['staff']['name']}</i>" \
            f"\n" \
            f"<b>Метро</b>: <i>{metro_station}</i>" \
            f"\n" \
            f"<b>Адрес</b>: <i>{company['address']}</i>" \
            f"\n" \
            f"<b>Стоимость</b>: <i>{total_cost}</i> рублей" \
            f"\n\n" \
            f"- - - - - - - - - - - - - - -" \
            f"\n\n"

    await callback.message.edit_text(
        text=text,
        parse_mode="HTML",
        reply_markup=keyboard.as_markup()
    )


def setup(dp: Dispatcher):
    dp.callback_query.register(start_handler, F.data.in_(config.EMOJI_NUMS))


