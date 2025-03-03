import typing
from aiogram import types, Dispatcher
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import select
from aiogram.fsm.context import FSMContext
from bot import models, filters, states
from bot.services import yclients
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, ReplyKeyboardBuilder, KeyboardButton
from aiogram import F
import re


async def add_admin_cmd_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    keyboard = InlineKeyboardBuilder()
    btn = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="admin_panel"
    )
    keyboard.row(btn)

    await callback.message.edit_text(
        text="Пришлите мне ID нового админа:",
        reply_markup=keyboard.as_markup()
    )
    await state.set_state(states.AddAdminStates.get_admin_id)


async def add_admin_handler(message: types.Message, state: FSMContext, session: sessionmaker):
    await state.clear()
    admin_id = message.text

    async with session() as open_session:
        admin: models.sql.Admin = await open_session.execute(
            select(models.sql.Admin).filter_by(id=int(admin_id)))
        admin = admin.scalars().first()

    if admin:
        keyboard = InlineKeyboardBuilder()
        btn = InlineKeyboardButton(
            text="◀️ Назад",
            callback_data="admin_panel"
        )
        keyboard.row(btn)
        btn = InlineKeyboardButton(
            text="Удалить админа",
            callback_data="delete_admin"
        )
        keyboard.row(btn)
        return await message.answer(
            text=f"Данный админ уже привязан к филлиалу {admin.company_title}. Для начала вам нужно его удалить.",
            reply_markup=keyboard.as_markup()
        )

    keyboard = InlineKeyboardBuilder()
    btn = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="admin_panel"
    )
    keyboard.row(btn)

    try:
        await message.bot.send_chat_action(chat_id=admin_id, action="typing")
    except Exception:
        return await message.answer(
            text="Не удалось добавить админа. Убедитесь что вы ввели правильный ID,"
                 " а также у админа есть чат с этим ботом.",
            reply_markup=keyboard.as_markup()
        )

    await message.answer(
        text="Теперь укажите ключевое слово студии, которое указано в названии ЛК YClients. "
             "Например: Менделеевская, Проспект Мира",
        reply_markup=keyboard.as_markup()
    )
    await state.update_data(dict(
        admin_id=int(admin_id)
    ))
    await state.set_state(states.AddAdminStates.get_company_id)


async def get_company_id_handler(message: types.Message, state: FSMContext, session):
    keyboard = InlineKeyboardBuilder()
    btn = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="admin_panel"
    )
    keyboard.row(btn)

    state_data = await state.get_data()

    response = await yclients.get_companies()
    companies: list = response["data"]

    match_title = [i for i in companies if re.findall(message.text, i["title"], flags=re.I)]
    match_address = [i for i in companies if re.findall(message.text, i["address"], flags=re.I)]

    if match_title:
        company = match_title[0]
    elif match_address:
        company = match_address[0]
    else:
        return await message.answer(
            text="Не нашли такую студию.",
            reply_markup=keyboard.as_markup()
        )

    await message.answer(
        text=f"Новый админ <b>{state_data.get('admin_id')}</b> добавлен в студию <b>{company['title']}</b>!\n\n"
             "Удалить админа /deleteadmin",
        parse_mode="HTML",
        reply_markup=keyboard.as_markup()
    )

    async with session() as open_session:
        new_admin = models.sql.Admin(
            id=state_data.get("admin_id"),
            company_id=company["id"],
            company_title=company["title"]
        )
        await open_session.merge(new_admin)
        await open_session.commit()


async def delete_admin_cmd_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    keyboard = InlineKeyboardBuilder()
    btn = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="admin_panel"
    )
    keyboard.row(btn)

    await callback.message.edit_text(
        text="Пришлите мне ID админа, которого нужно удалить:",
        reply_markup=keyboard.as_markup()
    )
    await state.set_state(states.DeleteAdminStates.get_admin_id)


async def delete_admin_handler(message: types.Message, state: FSMContext, session: sessionmaker):
    await state.clear()
    admin_id = message.text
    keyboard = InlineKeyboardBuilder()
    btn = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="admin_panel"
    )
    keyboard.row(btn)

    if not admin_id.isdecimal():
        return await message.answer(
            text="Не удалось удалить админа. Убедитесь что вы ввели правильный ID.",
            reply_markup=keyboard.as_markup()
        )

    admin_id = int(admin_id)

    async with session() as open_session:
        admin: models.sql.Admin = await open_session.execute(
            select(models.sql.Admin).filter_by(id=int(admin_id)))
        admin = admin.scalars().first()

        if not admin:
            await message.answer(
                text="Такого админа нету в базе!",
                reply_markup=keyboard.as_markup()
            )
        else:
            await open_session.delete(admin)
            await open_session.commit()
            await message.answer(
                text="Админ был удален.",
                reply_markup=keyboard.as_markup()
            )


def setup(dp: Dispatcher):
    dp.callback_query.register(
        add_admin_cmd_handler,
        F.data == "add_admin",
        filters.IsBotAdminFilter(True)
    )

    dp.message.register(
        add_admin_handler,
        states.AddAdminStates.get_admin_id,
        filters.IsBotAdminFilter(True)
    )

    dp.message.register(
        get_company_id_handler,
        states.AddAdminStates.get_company_id,
        filters.IsBotAdminFilter(True)
    )

    dp.callback_query.register(
        delete_admin_cmd_handler,
        F.data == "delete_admin",
        filters.IsBotAdminFilter(True)
    )

    dp.message.register(
        delete_admin_handler,
        states.DeleteAdminStates.get_admin_id,
        filters.IsBotAdminFilter(True)
    )

