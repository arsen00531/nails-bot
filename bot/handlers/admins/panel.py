from aiogram import types, Dispatcher
from bot import config
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, ReplyKeyboardBuilder, KeyboardButton
from sqlalchemy import select
from bot import models
from aiogram import F
import typing
from bot.services import yclients
from aiogram.fsm.context import FSMContext


async def panel_handler_message(message: types.Message, session, state: FSMContext):
    await state.clear()
    async with session() as open_session:
        admins: typing.List[int] = await open_session.execute(select(models.sql.Admin.id))
        admins = admins.scalars().all()

    keyboard = InlineKeyboardBuilder()

    if message.from_user.id in config.BOT_ADMINS:
        btn_2 = InlineKeyboardButton(
            text=f"Рассылка СЕТЬ",
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
            text="Добавить подробнее",
            callback_data="add_about"
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
        await state.update_data(company_id=admin.company_id)

        btn_1 = InlineKeyboardButton(
            text=f"Рассылка",
            callback_data=f"broadcast_company"
        )
        keyboard.row(btn_1)
        btn_2 = InlineKeyboardButton(
            text=f"Отзывы",
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

async def panel_handler_callback(callback: types.CallbackQuery, session, state: FSMContext):
    await state.clear()
    await callback.answer()
    async with session() as open_session:
        admins: typing.List[int] = await open_session.execute(select(models.sql.Admin.id))
        admins = admins.scalars().all()

    keyboard = InlineKeyboardBuilder()

    if callback.from_user.id in config.BOT_ADMINS:
        btn_2 = InlineKeyboardButton(
            text=f"Рассылка СЕТЬ",
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
            text="Добавить подробнее",
            callback_data="add_about"
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
        await callback.message.edit_text(
            text="<b>Админ панель</b>",
            reply_markup=keyboard.as_markup(),
            parse_mode="HTML"
        )
    elif callback.from_user.id in admins:
        async with session() as open_session:
            admin: models.sql.Admin = await open_session.execute(
                select(models.sql.Admin).filter_by(id=callback.from_user.id))
            admin = admin.scalars().first()

        response = await yclients.get_company(admin.company_id)
        await state.update_data(company_id=admin.company_id)

        btn_1 = InlineKeyboardButton(
            text=f"Рассылка",
            callback_data=f"broadcast_company"
        )
        keyboard.row(btn_1)
        btn_2 = InlineKeyboardButton(
            text=f"Отзывы",
            callback_data=f"yandex_company_{admin.company_id}"
        )
        keyboard.row(btn_2)

        btn = InlineKeyboardButton(
            text="◀️ Назад",
            callback_data="back_to_main"
        )
        keyboard.row(btn)

        await callback.message.edit_text(
            text="<b>Админ панель</b>\n\n"
                 f"Ваш филиал: <i>{response['data']['title']}</i>",
            reply_markup=keyboard.as_markup(),
            parse_mode="HTML"
        )


def setup(dp: Dispatcher):
    dp.message.register(panel_handler_message, F.text == "Админ панель ⚙️")
    dp.callback_query.register(panel_handler_callback, F.data == "admin_panel")
