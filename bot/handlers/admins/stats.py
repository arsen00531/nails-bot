import typing
from aiogram import types, Dispatcher, F
from aiogram.filters import Command
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import select, func

from bot import models, filters
import datetime


async def stats_message_handler(callback: types.CallbackQuery, session: sessionmaker):
    async with session() as open_session:
        users = await open_session.execute(
            select(models.sql.User))
        users = users.scalars().all()

    await callback.answer(
        text=f"Всего пользователей: {len(users)}\n",
        show_alert=True
    )


def setup(dp: Dispatcher):
    dp.callback_query.register(
        stats_message_handler,
        filters.IsBotAdminFilter(True),
        F.data == "stats"
    )

