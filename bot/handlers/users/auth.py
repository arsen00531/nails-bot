from aiogram import types, Dispatcher
from bot import keyboards, config, filters
from sqlalchemy import select
from bot import models
from datetime import datetime
from aiogram import F
import typing


async def contact_handler(message: types.Message, session):
    async with session() as open_session:
        admins: typing.List[models.sql.Admin] = await open_session.execute(select(
            models.sql.Admin.id))
        admins = admins.scalars().all()

    if (message.from_user.id in config.BOT_ADMINS) or (message.from_user.id in admins):
        keyboard = keyboards.reply.main_admin.keyboard
    else:
        keyboard = keyboards.reply.main.keyboard

    await message.delete()

    async with session() as open_session:
        new_user = models.sql.User(
            id=message.from_user.id,
            username=message.from_user.username,
            fullname=message.from_user.full_name[:50],
            phone=message.contact.phone_number,
            created_at=datetime.now()
        )

        await open_session.merge(new_user)
        await open_session.commit()

    await message.answer(
        text="Поздравляем с регистрацией.",
        reply_markup=keyboard
    )


def setup(dp: Dispatcher):
    dp.message.register(contact_handler, F.content_type == types.ContentType.CONTACT)


