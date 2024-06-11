from aiogram import Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message
import tools.filer
from sqlalchemy import select
from bot import keyboards, config, models
import datetime


async def cancel_handler(message: Message, state):
    await state.clear()
    await message.answer(
        text="Canceled.",
    )


def setup(dp: Dispatcher):
    dp.message.register(
        cancel_handler,
        Command("cancel")
    )

    


