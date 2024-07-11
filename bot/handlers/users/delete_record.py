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
    print(callback.data)
    record_id, company_id = re.findall("delete_record_(.+)_(.+)", callback.data)[0]
    keyboard = InlineKeyboardBuilder()
    btn = InlineKeyboardButton(
        text="Да, отменить",
        callback_data=f"delete_approve_record_{record_id}_{company_id}"
    )
    keyboard.row(btn)
    btn = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data=f"delete_cancel_record_{record_id}_{company_id}"
    )
    keyboard.row(btn)

    await callback.message.edit_text(
        text="Вы уверены что хотите отменить запись?",
        reply_markup=keyboard.as_markup()
    )


async def delete_approve_handler(callback: types.CallbackQuery, session):
    await callback.answer()
    record_id, company_id = re.findall("delete_approve_record_(.+)_(.+)", callback.data)[0]
    record_id = int(record_id)
    r = requests.get(f"https://api.yclients.com/api/v1/company/{company_id}?showBookforms=1", headers=config.YCLIENTS_HEADERS)

    web_app_info = types.WebAppInfo(url=r.json()["data"]["bookforms"][0]["url"])
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
    print(record_id, company_id)
    r = requests.delete(
        f"https://api.yclients.com/api/v1/record/{company_id}/{record_id}",
        headers=config.YCLIENTS_HEADERS
    )
    await callback.message.delete()
    await callback.message.answer(
        text="Запись <b>отменена</b>. Вы можете перезаписаться на другое время по кнопке ниже.",
        reply_markup=keyboard.as_markup(),
        parse_mode="HTML"
    )


async def delete_cancel_handler(callback: types.CallbackQuery, session):
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

    r = requests.get(
        f"https://api.yclients.com/api/v1/records/1042269?page=1&count=500&start_date={datetime_now.year}-{datetime_now_month}-{datetime_now_day}",
        headers=config.YCLIENTS_HEADERS
    )
    record_id, company_id = re.findall("delete_cancel_record_(.+)_(.+)", callback.data)[0]
    record = [record for record in r.json()["data"] if record["id"] == int(record_id)][0]

    web_app_info = types.WebAppInfo(url=record["short_link"])

    keyboard = InlineKeyboardBuilder()
    btn = InlineKeyboardButton(
        text="Отменить ❌",
        callback_data=f"delete_record_{record_id}_{company_id}"
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
        f"https://api.yclients.com/api/v1/companies?id={1042269}",
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
    dp.callback_query.register(start_handler, F.data.regexp(r"delete_record_(.+)"))
    dp.callback_query.register(delete_approve_handler, F.data.regexp(r"delete_approve_record_(.+)"))
    dp.callback_query.register(delete_cancel_handler, F.data.regexp(r"delete_cancel_record_(.+)"))


