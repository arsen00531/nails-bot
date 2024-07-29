from aiogram import types, Dispatcher
from aiogram.filters import CommandStart

import tools.filer
from bot import keyboards, config
from sqlalchemy import select
from bot import models
import typing


async def start_handler(message: types.Message, session):
    kb = [
        [
            types.KeyboardButton(text="Поделиться", request_contact=True),
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=False)
    await message.bot.set_chat_menu_button(chat_id=message.chat.id)

    async with session() as open_session:
        user: models.sql.User = await open_session.execute(select(
            models.sql.User).filter_by(id=message.from_user.id))
        user = user.scalars().first()
        admins: typing.List[models.sql.Admin] = await open_session.execute(select(
            models.sql.Admin.id))
        admins = admins.scalars().all()

    if not user:
        msg_text = await tools.filer.read_txt("start")
        photo = types.FSInputFile("bot/data/images/start.jpg")
        await message.answer_photo(
            photo=photo,
            caption=msg_text,
            reply_markup=keyboard
        )
    else:
        if (message.from_user.id in config.BOT_ADMINS) or (message.from_user.id in admins):
            keyboard = keyboards.reply.main_admin.keyboard
        else:
            keyboard = keyboards.reply.main.keyboard
        msg_text = await tools.filer.read_txt("start_auth")
        photo = types.FSInputFile("bot/data/images/start.jpg")

        await message.answer_photo(
            photo=photo,
            caption=msg_text,
            reply_markup=keyboard
        )


def setup(dp: Dispatcher):
    dp.message.register(start_handler, CommandStart())
