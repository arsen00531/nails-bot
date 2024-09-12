import typing
from aiogram import types, Dispatcher
from aiogram.filters import Command
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import select, func
from aiogram.fsm.context import FSMContext
from bot import models, filters, states
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, ReplyKeyboardBuilder, KeyboardButton
from aiogram import F
import re
import validators


async def yandex_company_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    company_id = int(re.findall(r"yandex_company_(.+)", callback.data)[0])
    keyboard = InlineKeyboardBuilder()
    btn = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="admin_panel"
    )
    keyboard.row(btn)

    await callback.message.edit_text(
        text="Пришлите мне ссылку отзывы вашего филиала.",
        reply_markup=keyboard.as_markup()
    )
    await state.update_data(dict(company_id=company_id))
    await state.set_state(states.YandexCompanyStates.get_url)


async def get_company_url_handler(message: types.Message, state: FSMContext, session):
    state_data = await state.get_data()
    company_id = state_data.get("company_id")

    keyboard = InlineKeyboardBuilder()
    btn = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="admin_panel"
    )
    keyboard.row(btn)

    if not validators.url(message.text):
        return await message.answer(
            text="Это не похоже на ссылку, попробуйте еще раз.",
            reply_markup=keyboard.as_markup()
        )

    await state.clear()

    async with session() as open_session:
        yandex_company = await open_session.execute(
            select(models.sql.YandexCompany).filter_by(company_id=company_id))
        yandex_company: models.sql.YandexCompany = yandex_company.scalars().first()

        if yandex_company:
            yandex_company.url = message.text
            await open_session.commit()
        else:
            new_company = models.sql.YandexCompany(
                company_id=company_id,
                url=message.text
            )
            await open_session.merge(new_company)
            await open_session.commit()

    await message.answer(
        text=f"Ссылка успешно добавлена.",
        parse_mode="HTML",
        reply_markup=keyboard.as_markup()
    )


def setup(dp: Dispatcher):
    dp.callback_query.register(
        yandex_company_handler,
        F.data.regexp("yandex_company_(.+)"),
    )

    dp.message.register(
        get_company_url_handler,
        states.YandexCompanyStates.get_url,
    )


