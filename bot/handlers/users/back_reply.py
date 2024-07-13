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
import pytz
import typing
from bot import keyboards


EMOJI_NUMS = [
    "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣",
]


async def start_handler(message: types.Message, state: FSMContext, session):
    await state.clear()
    async with session() as open_session:
        admins: typing.List[models.sql.Admin] = await open_session.execute(select(
            models.sql.Admin.id))
        admins = admins.scalars().all()

    if (message.from_user.id in config.BOT_ADMINS) or (message.from_user.id in admins):
        keyboard = keyboards.reply.main_admin.keyboard
    else:
        keyboard = keyboards.reply.main.keyboard

    await message.answer(
        text="Здравствуйте, вас приветствует сеть салонов City Nails.",
        reply_markup=keyboard
    )


async def back_to_records_handler(callback: types.CallbackQuery, state: FSMContext, session):
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

    records = [
        record for record in records
        if datetime.strptime(record["datetime"], "%Y-%m-%dT%H:%M:%S%z") > datetime_now
    ]

    if not records:
        await callback.message.delete()
        async with session() as open_session:
            admins: typing.List[models.sql.Admin] = await open_session.execute(select(
                models.sql.Admin.id))
            admins = admins.scalars().all()

        if (callback.from_user.id in config.BOT_ADMINS) or (callback.from_user.id in admins):
            keyboard = keyboards.reply.main_admin.keyboard
        else:
            keyboard = keyboards.reply.main.keyboard
        return await callback.message.answer(
            text="У вас нету активных записей на данный момент.",
            reply_markup=keyboard
        )

    n = 0
    temp_array = []
    keyboard = InlineKeyboardBuilder()
    buttons = []
    for e in EMOJI_NUMS[:len(records)]:
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

    btn = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="back_to_main"
    )
    keyboard.row(btn)

    await callback.message.edit_text(
        text=text,
        parse_mode="HTML",
        reply_markup=keyboard.as_markup(width=3)
    )


async def back_to_main(callback: types.CallbackQuery, state: FSMContext, session):
    await state.clear()
    await callback.answer()
    await callback.message.delete()

    async with session() as open_session:
        admins: typing.List[models.sql.Admin] = await open_session.execute(select(
            models.sql.Admin.id))
        admins = admins.scalars().all()

    if (callback.from_user.id in config.BOT_ADMINS) or (callback.from_user.id in admins):
        keyboard = keyboards.reply.main_admin.keyboard
    else:
        keyboard = keyboards.reply.main.keyboard

    await callback.message.answer(
        text="Здравствуйте, вас приветствует сеть салонов City Nails.",
        reply_markup=keyboard
    )

def setup(dp: Dispatcher):
    dp.message.register(start_handler, F.text == "◀️ Назад")
    dp.callback_query.register(back_to_records_handler, F.data == "back_to_records")
    dp.callback_query.register(back_to_main, F.data == "back_to_main")
