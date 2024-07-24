import asyncio
import re
from aiogram import types, Dispatcher
from bot import keyboards, config
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from sqlalchemy import select
from bot import models
from aiogram import F
from bot import states


async def support_handler(callback: types.CallbackQuery, state: FSMContext, session):
    await callback.answer()
    async with session() as open_session:
        user: models.sql.User = await open_session.execute(select(
            models.sql.User).filter_by(id=callback.from_user.id))
        user = user.scalars().first()

        if user.company_id:
            admins: models.sql.Admin = await open_session.execute(select(
                models.sql.Admin).filter_by(company_id=user.company_id))
            admins: list = admins.scalars().all()
            admins.reverse()
            admin = admins[0]

    if not user.company_id:
        return await callback.message.answer(
            text="Не можем определить к какому салону вы относитесь."
                 " Сделайте запись, чтобы связаться с нужным салоном"
        )

    keyboard = InlineKeyboardBuilder()
    btn = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="back_to_main"
    )
    keyboard.row(btn)

    await callback.message.answer(
        text="Чат запущен!\n\n"
             "Введите сообщение для поддержки.",
        reply_markup=keyboard.as_markup()
    )
    await state.update_data(chat_id=admin.id)
    await state.set_state(states.AdminSupportStates.get_msg)


async def chat_answer_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()

    chat_id = int(re.findall(r"chat_answer_to_(.+)", callback.data)[0])

    await callback.message.answer(
        text="Введите ответ",
    )
    await state.update_data(chat_id=chat_id)
    await state.set_state(states.AdminSupportStates.get_msg)


async def get_msg_handler(message: types.Message, state: FSMContext, session):
    state_data = await state.get_data()
    await state.clear()

    async with session() as open_session:
        user: models.sql.User = await open_session.execute(select(
            models.sql.User).filter_by(id=message.from_user.id))
        user = user.scalars().first()

        admins: models.sql.Admin = await open_session.execute(select(
            models.sql.Admin))
        admins: list[models.sql.Admin] = admins.scalars().all()
        admins_id = [a.id for a in admins]

    keyboard = InlineKeyboardBuilder()
    btn = InlineKeyboardButton(
        text="Ответить",
        callback_data=f"chat_answer_to_{message.from_user.id}"
    )
    keyboard.row(btn)

    if message.from_user.id in admins_id:
        company_title = [a.company_title for a in admins if a.id == message.from_user.id][0]
        await message.bot.send_message(
            chat_id=state_data["chat_id"],
            text=f"Сообщение от: <b>{company_title}</b>",
            parse_mode="HTML"
        )
    else:
        await message.bot.send_message(
            chat_id=state_data["chat_id"],
            text=f"Сообщение от: <b>{message.from_user.full_name[:30]}</b>"
                 f"\n"
                 f"Номер телефона: <i>+{user.phone}</i>",
            parse_mode="HTML"
        )

    await asyncio.sleep(0.5)
    await message.send_copy(
        chat_id=state_data["chat_id"],
        reply_markup=keyboard.as_markup()
    )
    if (message.from_user.id in config.BOT_ADMINS) or (message.from_user.id in admins_id):
        keyboard = keyboards.reply.main_admin.keyboard
    else:
        keyboard = keyboards.reply.main.keyboard

    await message.answer(
        text="Сообщение отправлено, ожидайте ответа.",
        reply_markup=keyboard
    )


def setup(dp: Dispatcher):
    dp.callback_query.register(support_handler, F.data == "admin_support")
    dp.callback_query.register(chat_answer_handler, F.data.regexp("chat_answer_to_(.+)"))
    dp.message.register(get_msg_handler, states.AdminSupportStates.get_msg)


