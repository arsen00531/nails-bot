from aiogram.fsm.context import FSMContext
from aiogram import types, Dispatcher, F
from aiogram.types import CallbackQuery, Message
import typing
from bot import states
from bot import models, filters
from bot.services.broadcaster import BaseBroadcaster
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from sqlalchemy import select
from bot.services import yclients


async def get_msg_handler(message: types.Message, state: FSMContext):
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
        callback_data="admin_panel"
    )
    keyboard.row(btn_start)
    keyboard.row(btn_cancel)

    await message.answer(
        "[2/2] Запустить расссылку?",
        reply_markup=keyboard.as_markup(),
    )
    await state.update_data(dict(message=message))
    await state.set_state(states.BroadcastStates.broadcast)


async def get_text_handler(message: Message, state: FSMContext):
    state_data = await state.get_data()
    broadcast_spec: str = state_data.get("broadcast_spec")

    photo = types.FSInputFile(f"bot/data/images/{broadcast_spec}.jpg")
    send_message = await message.answer_photo(
        photo=photo,
        caption=message.html_text
    )
    keyboard = InlineKeyboardBuilder()
    btn_start = InlineKeyboardButton(
        text="Запустить", callback_data="run_broadcast"
    )
    btn_cancel = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="admin_panel"
    )
    keyboard.row(btn_start)
    keyboard.row(btn_cancel)

    await message.answer(
        "[2/2] Запустить расссылку?",
        reply_markup=keyboard.as_markup(),
    )
    await state.update_data(dict(message=send_message))
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
        callback_data="admin_panel"
    )
    keyboard.row(btn_cancel)

    company_name = "СЕТЬ"
    async with session() as open_session:
        if company_id:
            users: typing.List[int] = await open_session.execute(
                select(models.sql.User.id).filter_by(company_id=int(company_id))
            )
            users = users.scalars().all()
            response = await yclients.get_company(company_id)
            company_name = response["data"]["title"]
        else:
            users: typing.List[int] = await open_session.execute(select(models.sql.User.id))
            users = users.scalars().all()

    users = set(users)
    await callback.message.answer(
        text=f"Рассылка запущена в <b>{company_name}</b>. Кол-во пользователей: {len(users)}",
        reply_markup=keyboard.as_markup(),
        parse_mode="HTML"
    )

    broadcaster = BaseBroadcaster(chats_id=users, message=message)
    success_count = await broadcaster.run()
    await callback.message.answer(
        "Рассылка завершилась в <b>{}</b>.\n"
        "Отправлено сообщений: {} / {}".format(company_name, success_count, len(users)),
        parse_mode="HTML"
    )


def setup(dp: Dispatcher):
    dp.message.register(
        get_text_handler,
        states.BroadcastStates.get_text,
    )
    dp.message.register(
        get_msg_handler,
        states.BroadcastStates.get_msg,
    )
    dp.callback_query.register(
        run_broadcast_handler,
        states.BroadcastStates.broadcast,
    )
