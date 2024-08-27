from aiogram import types, Dispatcher
from bot import config
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, ReplyKeyboardBuilder, KeyboardButton
from sqlalchemy import select
from bot import models
from aiogram import F
import typing
from bot.services import yclients


async def start_handler(message: types.Message, session):
    async with session() as open_session:
        admins: typing.List[int] = await open_session.execute(select(models.sql.Admin.id))
        admins = admins.scalars().all()

    keyboard = InlineKeyboardBuilder()

    if message.from_user.id in config.BOT_ADMINS:
        btn_2 = InlineKeyboardButton(
            text=f"Рассылка",
            callback_data="broadcast_all"
        )
        keyboard.row(btn_2)
        btn_2 = InlineKeyboardButton(
            text=f"Рассылка ФИЛИАЛ",
            callback_data="broadcast_company"
        )
        keyboard.row(btn_2)

        btn = InlineKeyboardButton(
            text="Добавить админа",
            callback_data="add_admin"
        )
        keyboard.row(btn)

        btn = InlineKeyboardButton(
            text="Удалить админа",
            callback_data="delete_admin"
        )
        keyboard.row(btn)

        btn = InlineKeyboardButton(
            text="Статистика",
            callback_data="stats"
        )
        keyboard.row(btn)
        btn = InlineKeyboardButton(
            text="◀️ Назад",
            callback_data="back_to_main"
        )
        keyboard.row(btn)
        await message.answer(
            text="<b>Админ панель</b>",
            reply_markup=keyboard.as_markup(),
            parse_mode="HTML"
        )
    elif message.from_user.id in admins:
        async with session() as open_session:
                admin: models.sql.Admin = await open_session.execute(
                    select(models.sql.Admin).filter_by(id=message.from_user.id))
                admin = admin.scalars().first()

        response = await yclients.get_company(admin.company_id)

        btn_1 = InlineKeyboardButton(
            text=f"Рассылка ФИЛИАЛ",
            callback_data=f"broadcast_company_{admin.company_id}"
        )
        keyboard.row(btn_1)
        btn_2 = InlineKeyboardButton(
            text=f"Отзывы Яндекс",
            callback_data=f"yandex_company_{admin.company_id}"
        )
        keyboard.row(btn_2)

        btn = InlineKeyboardButton(
            text="◀️ Назад",
            callback_data="back_to_main"
        )
        keyboard.row(btn)

        await message.answer(
            text="<b>Админ панель</b>\n\n"
                 f"Ваш филиал: <i>{response['data']['title']}</i>",
            reply_markup=keyboard.as_markup(),
            parse_mode="HTML"
        )


def setup(dp: Dispatcher):
    dp.message.register(start_handler, F.text == "Админ панель ⚙️")
