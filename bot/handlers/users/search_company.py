from aiogram import types, Dispatcher
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from aiogram import F
from aiogram.fsm.context import FSMContext
from bot.states import FindCompanyStates
from bot.services import yclients
import re


async def search_company_handler(message: types.Message, state: FSMContext):
    keyboard = InlineKeyboardBuilder()
    btn = InlineKeyboardButton(
        text="Выход",
        callback_data="back_to_main"
    )
    keyboard.row(btn)

    await message.answer(
        text="Отправьте <b>станцию метро</b>\n"
             "<i>(например: Менделеевская)</i>\n\n"
             "Или <b>название улицы</b> салона\n"
             "<i>(например: Тверская-Ямская)</i>",
        reply_markup=keyboard.as_markup()
    )
    await state.set_state(FindCompanyStates.get_data)


async def get_data_handler(message: types.Message, state: FSMContext):
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
            callback_data="back_to_main"
        )
        keyboard.row(btn)
        return await message.answer(
            text="Не нашли такой салон.",
            reply_markup=keyboard.as_markup()
        )

    keyboard = InlineKeyboardBuilder()

    btn_1 = InlineKeyboardButton(
        text="Написать администратору 📩",
        callback_data=f"chat_answer_to_{company['id']}"
    )
    keyboard.row(btn_1)
    btn_2 = InlineKeyboardButton(
        text="Подробнее",
        url="https://citynails.studio/"
    )

    web_app_info = types.WebAppInfo(url=company["bookforms"][0]["url"])
    btn_3 = InlineKeyboardButton(
        text="Записаться",
        web_app=web_app_info
    )
    keyboard.row(btn_2, btn_3)

    btn = InlineKeyboardButton(
        text="Выход",
        callback_data="back_to_main"
    )
    keyboard.row(btn)

    await message.answer_venue(
        title=company["title"],
        address=company["address"],
        latitude=company["coordinate_lat"],
        longitude=company["coordinate_lon"],
        reply_markup=keyboard.as_markup()
    )


def setup(dp: Dispatcher):
    dp.message.register(search_company_handler, F.text == "Поиск 🔎")
    dp.message.register(get_data_handler, FindCompanyStates.get_data)
