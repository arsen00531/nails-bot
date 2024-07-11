import asyncio
from datetime import datetime, timedelta
import typing
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, ReplyKeyboardBuilder, KeyboardButton

import requests

from bot import models
from sqlalchemy import select
from aiogram import Bot
import pytz
from bot import config
from aiogram import types


async def send_message(user_id, record, bot: Bot, session):
    res = requests.get(
        f"https://api.yclients.com/api/v1/company/{record['company_id']}/",
        headers=config.YCLIENTS_HEADERS
    )
    company = res.json()["data"]

    datetime_object = datetime.strptime(record["datetime"], "%Y-%m-%dT%H:%M:%S%z")
    datetime_minute = datetime_object.minute
    if datetime_minute < 10:
        datetime_minute = f"0{datetime_minute}"

    keyboard = InlineKeyboardBuilder()
    btn = InlineKeyboardButton(
        text="Отменить ❌",
        callback_data=f"delete_record_{record['id']}_{record['company_id']}"
    )
    keyboard.row(btn)
    btn = InlineKeyboardButton(
        text="Связаться с администратором",
        callback_data="admin_support"
    )
    keyboard.row(btn)

    await bot.send_message(
        chat_id=user_id,
        text=f"Приветствуем, на связи {company['title']} 👋\n"
             f"❗️Напоминаем о записи {datetime_object.day} {config.MONTHS[datetime_object.month]} в {datetime_object.hour}:{datetime_minute} МСК\n\n"
             f"<b>Мастер</b>: <i>{record['staff']['name']}</i>\n"
             f"<b>Адрес</b>: <i>{company['address']}</i>",
        reply_markup=keyboard.as_markup(),
        parse_mode="HTML"
    )


async def send_message2(user_id, record, bot: Bot, session):
    async with (session() as open_session):
        yandex_company = await open_session.execute(
            select(models.sql.YandexCompany).filter_by(company_id=record["company_id"]))
        yandex_company: models.sql.YandexCompany = yandex_company.scalars().first()

    keyboard = InlineKeyboardBuilder()
    btn = InlineKeyboardButton(
        text="Оставить отзыв",
        url=yandex_company.url
    )
    keyboard.row(btn)

    await bot.send_message(
        chat_id=user_id,
        text=f"Приветствуем, на связи {record['title']} 👋\n\n"
             f"Вам все понравилось? Пожалуйста, оцените нашу работу оставив отзыв.",
        reply_markup=keyboard.as_markup()
    )


async def send_message3(user_id, record, bot: Bot):
    res = requests.get(
        f"https://api.yclients.com/api/v1/company/{record['company_id']}/",
        headers=config.YCLIENTS_HEADERS
    )
    company = res.json()["data"]
    web_app_info = types.WebAppInfo(url=company["bookforms"][0]["url"])
    keyboard = InlineKeyboardBuilder()
    btn = InlineKeyboardButton(
        text="Записаться",
        web_app=web_app_info
    )
    keyboard.row(btn)

    await bot.send_message(
        chat_id=user_id,
        text=f"Приветствуем, на связи {record['title']}. Что-то вы давненько у нас не были 😃\n\n"
             f"Запишитесь онлайн прямо сейчас по кнопке ниже!",
        reply_markup=keyboard.as_markup()
    )


async def notify_sender(session, bot):
    async with (session() as open_session):
        records = await open_session.execute(select(models.sql.Record))
        records: typing.List[models.sql.Record] = records.scalars().all()
        datetime_now = datetime.now(pytz.timezone('Europe/Moscow'))

        for r in records:
            notification_intervals = [
                timedelta(minutes=25),
                timedelta(minutes=15)
            ]

            await asyncio.sleep(1)
            res = requests.get(
                f"https://api.yclients.com/api/v1/record/{r.company_id}/{r.id}",
                headers=config.YCLIENTS_HEADERS
            )
            record = res.json()["data"]
            if record["deleted"]:
                continue

            datetime_record = datetime.strptime(r.datetime, "%Y-%m-%dT%H:%M:%S%z")
            # datetime_record = datetime.strptime("2024-07-08T11:00:00+03:00", "%Y-%m-%dT%H:%M:%S%z")
            # last_notification_time = datetime.strptime("2024-07-08T10:45:00+03:00", "%Y-%m-%dT%H:%M:%S%z")
            last_notification_time = datetime.strptime(
                r.last_notification, "%Y-%m-%dT%H:%M:%S%z"
            ) if r.last_notification else None

            if last_notification_time:
                if (datetime_now - last_notification_time) > timedelta(minutes=30) and (not r.post_notification_1):
                    res = requests.get(
                        f"https://api.yclients.com/api/v1/record/{r.company_id}/{r.id}",
                        headers=config.YCLIENTS_HEADERS
                    )
                    record_attendance = res.json()["data"]["attendance"]

                    if record_attendance == 1:
                        await send_message2(r.user_id, record, bot, session)
                        r.post_notification_1 = True
                        await open_session.commit()

                elif (datetime_now - last_notification_time) > timedelta(minutes=15) and (not r.post_notification_2):
                    res = requests.get(
                        f"https://api.yclients.com/api/v1/record/{r.company_id}/{r.id}",
                        headers=config.YCLIENTS_HEADERS
                    )
                    record_attendance = res.json()["data"]["attendance"]
                    if record_attendance == 1:
                        await send_message3(r.user_id, record, bot)
                        await open_session.delete(r)
                        await open_session.commit()

            for interval in notification_intervals:
                await asyncio.sleep(0.1)
                if last_notification_time is None or (datetime_record - last_notification_time) >= interval:
                    if (datetime_record - datetime_now) < interval and \
                            (interval - (datetime_record - datetime_now)) < timedelta(minutes=5):

                        await send_message(r.user_id, record, bot, session)
                        r.last_notification = datetime_now.strftime("%Y-%m-%dT%H:%M:%S%z")
                        await open_session.commit()
                        break

