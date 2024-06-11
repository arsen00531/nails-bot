import typing
from aiogram import types, Dispatcher
from aiogram.filters import Command
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import select, func

from bot import models, filters

import datetime


async def stats_message_handler(message: types.Message, session: sessionmaker):
    async with session() as open_session:
        users = await open_session.execute(
            select(models.sql.User))
        users = users.scalars().all()

    current_date = datetime.date.today()
    month_ago = current_date - datetime.timedelta(days=30)
    users_in_month = [user for user in users if month_ago <= user.created_at <= current_date]

    week_ago = current_date - datetime.timedelta(days=7)
    users_in_week = [user for user in users if week_ago <= user.created_at <= current_date]

    day_ago = current_date - datetime.timedelta(days=1)
    users_in_day = [user for user in users if day_ago <= user.created_at <= current_date]

    await message.answer(
        text=f"Total users: {len(users)}\n"
             f"Month: {len(users_in_month)}\n"
             f"Week: {len(users_in_week)}\n"
             f"Day: {len(users_in_day)}"
    )


def setup(dp: Dispatcher):
    dp.message.register(
        stats_message_handler,
        Command(commands="stats"),
        filters.IsBotAdminFilter(True)
    )

