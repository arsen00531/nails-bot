from aiogram import types, Dispatcher
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from aiogram import F
from sqlalchemy import select
from bot import models
from bot.services.haversine_formula import get_nearest_location
import re
from bot.services import yclients


async def location_handler(message: types.Message):
    user_location = {
        'lat': message.location.latitude,
        'lon': message.location.longitude
    }

    response = await yclients.get_companies()
    companies: list = response["data"]

    nearest_companies: list = get_nearest_location(companies, user_location)
    keyboard = InlineKeyboardBuilder()
    for company in nearest_companies:
        company_title = company["title"]
        company_id = company["id"]
        
        btn = InlineKeyboardButton(
            text=f"{company_title}",
            callback_data=f"near_company_{company_id}"
        )
        keyboard.row(btn)

    btn = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="back_to_main"
    )
    keyboard.row(btn)

    photo = types.FSInputFile("bot/data/images/nearest_company.png")
    await message.answer_photo(
        photo=photo,
        reply_markup=keyboard.as_markup()
    )


async def select_company_handler(callback: types.CallbackQuery, session):
    await callback.answer()
    await callback.message.delete()

    response = await yclients.get_companies()
    companies: list = response["data"]

    company_id = re.findall(r"near_company_(.+)", callback.data)[0]
    company = [c for c in companies if c["id"] == int(company_id)][0]

    async with session() as open_session:
        about_company = await open_session.execute(
            select(models.sql.AboutCompany).filter_by(company_id=int(company_id)))
        about_company: models.sql.AboutCompany = about_company.scalars().first()

    keyboard = InlineKeyboardBuilder()

    btn_1 = InlineKeyboardButton(
        text="Написать администратору 📩",
        callback_data=f"chat_answer_to_{company_id}"
    )
    keyboard.row(btn_1)

    if about_company:
        web_app_info = types.WebAppInfo(url=about_company.url)
        btn_2 = InlineKeyboardButton(
            text="Подробнее",
            web_app=web_app_info
        )
    else:
        web_app_info = types.WebAppInfo(url="https://citynails.studio/")
        btn_2 = InlineKeyboardButton(
            text="Подробнее",
            web_app=web_app_info
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

    await callback.message.answer_venue(
        title=company["title"],
        address=company["address"],
        latitude=company["coordinate_lat"],
        longitude=company["coordinate_lon"],
        reply_markup=keyboard.as_markup()
    )


def setup(dp: Dispatcher):
    dp.message.register(location_handler, F.content_type == types.ContentType.LOCATION)
    dp.callback_query.register(select_company_handler, F.data.regexp(r"near_company_(.+)"))


