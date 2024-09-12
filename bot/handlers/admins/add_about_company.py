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
from bot.services import yclients


async def add_about_company(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    keyboard = InlineKeyboardBuilder()
    btn_2 = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="admin_panel"
    )
    keyboard.row(btn_2)

    await callback.message.edit_text(
        text="Укажите ключевое слово студии, которое указано в названии ЛК YClients. "
             "Например: Менделеевская, Проспект Мира",
        reply_markup=keyboard.as_markup()
    )
    await state.set_state(states.AboutCompanyStates.get_company_id)


async def get_company_id_handler(message: types.Message, state: FSMContext, session):
    await state.clear()
    response = await yclients.get_companies()
    companies = response["data"]

    match_title = [i for i in companies if re.findall(message.text, i["title"], flags=re.I)]
    match_address = [i for i in companies if re.findall(message.text, i["address"], flags=re.I)]

    if match_title:
        company = match_title[0]
    elif match_address:
        company = match_address[0]
    else:
        keyboard = InlineKeyboardBuilder()
        btn = InlineKeyboardButton(
            text="Выход",
            callback_data="admin_panel"
        )
        keyboard.row(btn)
        return await message.answer(
            text="Не нашли такую студию.",
            reply_markup=keyboard.as_markup()
        )
    keyboard = InlineKeyboardBuilder()
    btn_1 = InlineKeyboardButton(
        text="Далее",
        callback_data=f"add_about_company_{company['id']}"
    )
    keyboard.row(btn_1)
    btn_2 = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="admin_panel"
    )
    keyboard.row(btn_2)

    await message.answer(
        text=f"Студия {company['title']}, все верно?",
        reply_markup=keyboard.as_markup()
    )

async def add_about_company_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    company_id = int(re.findall(r"add_about_company_(.+)", callback.data)[0])
    keyboard = InlineKeyboardBuilder()
    btn = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="admin_panel"
    )
    keyboard.row(btn)

    await callback.message.edit_text(
        text="Пришлите мне ссылку.",
        reply_markup=keyboard.as_markup()
    )
    await state.update_data(dict(company_id=company_id))
    await state.set_state(states.AboutCompanyStates.get_url)


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
        about_company = await open_session.execute(
            select(models.sql.AboutCompany).filter_by(company_id=int(company_id)))
        about_company: models.sql.AboutCompany = about_company.scalars().first()

        if about_company:
            about_company.url = message.text
            await open_session.commit()
        else:
            new_company = models.sql.AboutCompany(
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
        add_about_company,
        F.data == "add_about"
    )

    dp.message.register(
        get_company_id_handler,
        states.AboutCompanyStates.get_company_id,
    )

    dp.callback_query.register(
        add_about_company_handler,
        F.data.regexp("add_about_company_(.+)"),
    )

    dp.message.register(
        get_company_url_handler,
        states.AboutCompanyStates.get_url,
    )


