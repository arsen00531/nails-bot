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
import typing




async def start_handler(message: types.Message, session):

    async with session() as open_session:
        user: models.sql.User = await open_session.execute(select(
            models.sql.User).filter_by(id=message.from_user.id))
        user = user.scalars().first()

        admins: typing.List[models.sql.Admin] = await open_session.execute(select(
            models.sql.Admin.id))
        admins = admins.scalars().all()

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

    records = [record for record in r.json()["data"] if (record["client"]["phone"] == user.phone) and not record["deleted"]]

    records = records[:9]

    records = [
        record for record in records
        if datetime.strptime(record["datetime"], "%Y-%m-%dT%H:%M:%S%z") > datetime_now
    ]

    if not records:
        if (message.from_user.id in config.BOT_ADMINS) or (message.from_user.id in admins):
            keyboard = keyboards.reply.main_admin.keyboard
        else:
            keyboard = keyboards.reply.main.keyboard

        return await message.answer(
            text="У вас нету активных записей на данный момент.",
            reply_markup=keyboard
        )

    n = 0
    temp_array = []
    keyboard = InlineKeyboardBuilder()
    buttons = []
    for e in config.EMOJI_NUMS[:len(records)]:
        btn = InlineKeyboardButton(
            text=e,
            callback_data=e
        )
        keyboard.add(btn)
        # temp_array.append(types.KeyboardButton(text=e))
        if n == 2:
            buttons.append(temp_array)
            temp_array = []
            n = 0
        else:
            n += 1

    # if n != 0:
    #     buttons.append(temp_array)
    #
    #

    print(records)
    text = ""
    for index, record in enumerate(records):
        datetime_object = datetime.strptime(record["datetime"], "%Y-%m-%dT%H:%M:%S%z")
        datetime_minute = datetime_object.minute
        if datetime_minute < 10:
            datetime_minute = f"0{datetime_minute}"

        record_titles = [s["title"] for s in record['services']]
        record_titles_string = " + ".join(record_titles)
        text += f"{config.EMOJI_NUMS[index]} <b>{record_titles_string}</b>\n\n" \
                 f"<b>Время</b>: <i>{datetime_object.day} {config.MONTHS[datetime_object.month]} в {datetime_object.hour}:{datetime_minute} МСК</i>" \
                 f"\n" \
                 f"<b>Мастер</b>: <i>{record['staff']['name']}</i>" \
                 f"\n\n" \
                 f"- - - - - - - - - - - - - - -" \
                 f"\n\n"

    keyboard.adjust(3)

    btn = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="back_to_main"
    )
    keyboard.row(btn)

    await message.answer(
        text=text,
        parse_mode="HTML",
        reply_markup=keyboard.as_markup()
    )


def setup(dp: Dispatcher):
    dp.message.register(start_handler, F.text == "Мои записи")


