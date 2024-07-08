import enum
import re

from aiogram.fsm.context import FSMContext
from aiogram import types, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from bot import keyboards
import typing
from bot import states
from bot import models, filters
from bot.services.broadcaster import BaseBroadcaster
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from sqlalchemy import select
import validators
from bot import config
import requests



async def broadcast_all_handler(callback: CallbackQuery, state: FSMContext, session):
    await callback.answer()

    keyboard = InlineKeyboardBuilder()
    btn_cancel = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="back_to_main"
    )
    keyboard.row(btn_cancel)

    await callback.message.edit_text(
        "[1/2] Пришлите мне сообщение, которое хотите отправить.",
        reply_markup=keyboard.as_markup()
    )
    await state.set_state(states.BroadcastStates.get_msg)


async def broadcast_company_id_handler(callback: CallbackQuery, state: FSMContext, session):
    await callback.answer()

    keyboard = InlineKeyboardBuilder()
    btn_cancel = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="back_to_main"
    )
    keyboard.row(btn_cancel)

    await callback.message.edit_text(
        "[1/2] Пришлите мне сообщение, которое хотите отправить.",
        reply_markup=keyboard.as_markup()
    )
    company_id = re.findall(r"broadcast_company_(\d+)", callback.data)
    if company_id:
        await state.update_data(dict(
            company_id=company_id[0]
        ))
    else:
        await state.update_data(dict(
            company_id=company_id
        ))
    await state.set_state(states.BroadcastStates.get_msg)


async def broadcast_company_handler(callback: CallbackQuery, state: FSMContext, session):
    await callback.answer()
    keyboard = InlineKeyboardBuilder()
    btn_cancel = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="back_to_main"
    )
    keyboard.row(btn_cancel)

    await callback.message.edit_text(
        text="Теперь укажите ключевое слово салона, которое указано в названии ЛК YClients. "
             "Например: Менделеевская, Проспект Мира",
        reply_markup=keyboard.as_markup()
    )

    await state.set_state(states.BroadcastStates.get_company_id)


async def get_company_id_handler(message: types.Message, state: FSMContext):
    await state.clear()
    keyboard = InlineKeyboardBuilder()
    btn_cancel = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="back_to_main"
    )
    keyboard.row(btn_cancel)
    r = requests.get(
        "https://api.yclients.com/api/v1/companies?my=1&count=100",
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
            text="Не нашли такой салон.",
            reply_markup=keyboard.as_markup()
        )

    keyboard = InlineKeyboardBuilder()
    btn = InlineKeyboardButton(
        text=f"Рассылка {salon['title']}",
        callback_data=f"broadcast_company_{salon['id']}"
    )
    keyboard.row(btn)
    btn_cancel = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="back_to_main"
    )
    keyboard.row(btn_cancel)
    await message.answer(
        text=f"Для запуска рассылки в {salon['title']} нажмите кнопку ниже.",
        reply_markup=keyboard.as_markup()
    )


async def get_msg_handler(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    broadcaster = BaseBroadcaster(
        chats_id=[message.from_user.id],
        message=message,
        disable_web_page_preview=True
    )

    await broadcaster.run()

    keyboard = InlineKeyboardBuilder()
    btn_start = InlineKeyboardButton(
        text="Запустить", callback_data="run_broadcast"
    )
    btn_cancel = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="back_to_main"
    )
    keyboard.row(btn_start)
    keyboard.row(btn_cancel)

    await message.answer(
        "[2/2] Запустить расссылку?",
        reply_markup=keyboard.as_markup(),
    )
    await state.update_data(dict(message=message))
    await state.set_state(states.BroadcastStates.broadcast)


async def run_broadcast_handler(callback: types.CallbackQuery, state: FSMContext, session):
    state_data = await state.get_data()
    message: types.Message = state_data.get("message")
    company_id = state_data.get("company_id")

    await state.clear()
    await callback.answer()
    await callback.message.delete()

    keyboard = InlineKeyboardBuilder()
    btn_cancel = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="back_to_main"
    )
    keyboard.row(btn_cancel)

    name = "СЕТЬ"
    async with session() as open_session:
        if company_id:
            users: typing.List[int] = await open_session.execute(
                select(models.sql.User.id).filter_by(company_id=int(company_id))
            )
            users = users.scalars().all()
            r = requests.get(
                f"https://api.yclients.com/api/v1/company/{company_id}",
                headers=config.YCLIENTS_HEADERS
            )
            name = r.json()["data"]["title"]
        else:
            users: typing.List[int] = await open_session.execute(select(models.sql.User.id))
            users = users.scalars().all()

    users = set(users)
    await callback.message.answer(
        text=f"Рассылка запущена в <b>{name}</b>. Кол-во пользователей: {len(users)}",
        reply_markup=keyboard.as_markup(),
        parse_mode="HTML"
    )

    broadcaster = BaseBroadcaster(chats_id=users, message=message)
    success_count = await broadcaster.run()
    await callback.message.answer(
        "Рассылка завершилась в <b>{}</b>.\n"
        "Отправлено сообщений: {} / {}".format(name, success_count, len(users)),
        parse_mode="HTML"
    )


def setup(dp: Dispatcher):
    dp.callback_query.register(
        broadcast_all_handler, F.data == "broadcast_all",
    )
    dp.callback_query.register(
        broadcast_company_handler, F.data == "broadcast_company",
   )
    dp.callback_query.register(
        broadcast_company_id_handler, F.data.regexp(r"broadcast_company_(\d+)"),
    )
    dp.message.register(
        get_company_id_handler,
        states.BroadcastStates.get_company_id,
    )
    dp.message.register(
        get_msg_handler,
        states.BroadcastStates.get_msg,
    )
    dp.callback_query.register(
        run_broadcast_handler,
        states.BroadcastStates.broadcast,
    )
