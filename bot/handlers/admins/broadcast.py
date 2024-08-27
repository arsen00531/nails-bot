import re
from aiogram.fsm.context import FSMContext
from aiogram import types, Dispatcher, F
from aiogram.types import CallbackQuery, Message
import typing
from bot import states
from bot import models, filters
from bot.services.broadcaster import BaseBroadcaster
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from sqlalchemy import select
from bot.services import yclients


async def broadcast_all_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    keyboard = InlineKeyboardBuilder()
    btn_1 = InlineKeyboardButton(
        text="Общая",
        callback_data="broadcast_all_all"
    )
    btn_2 = InlineKeyboardButton(
        text="Комбо услуга",
        callback_data="broadcast_all_combo"
    )
    keyboard.row(btn_1, btn_2)
    btn_3 = InlineKeyboardButton(
        text="Новая услуга",
        callback_data="broadcast_all_new_service"
    )
    btn_4 = InlineKeyboardButton(
        text="Новый салон",
        callback_data="broadcast_all_new_company"
    )
    keyboard.row(btn_3, btn_4)
    btn_cancel = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="back_to_main"
    )
    keyboard.row(btn_cancel)

    await callback.message.edit_text(
        "Выберите необходимую категорию рассылки ниже 👇",
        reply_markup=keyboard.as_markup()
    )


async def broadcast_company_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    keyboard = InlineKeyboardBuilder()
    btn_1 = InlineKeyboardButton(
        text="Общая",
        callback_data="broadcast_company_all"
    )
    btn_2 = InlineKeyboardButton(
        text="Комбо услуга",
        callback_data="broadcast_company_combo"
    )
    keyboard.row(btn_1, btn_2)
    btn_3 = InlineKeyboardButton(
        text="Новая услуга",
        callback_data="broadcast_company_new_service"
    )
    btn_4 = InlineKeyboardButton(
        text="Новый салон",
        callback_data="broadcast_company_new_company"
    )
    keyboard.row(btn_3, btn_4)
    btn_cancel = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="back_to_main"
    )
    keyboard.row(btn_cancel)

    await callback.message.edit_text(
        "Выберите необходимую категорию рассылки ниже 👇",
        reply_markup=keyboard.as_markup()
    )


async def broadcast_all_all_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    keyboard = InlineKeyboardBuilder()
    btn_cancel = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="back_to_main"
    )
    keyboard.row(btn_cancel)

    await callback.message.edit_text(
        "[1/2] Пришлите сюда сообщение, которое хотите отправить ✉️\n\n"
        "<i>При необходимости добавления кнопок — воспользуйтесь сервисом @posted</i>",
        reply_markup=keyboard.as_markup()
    )
    await state.set_state(states.BroadcastStates.get_msg)


async def broadcast_all_spec_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    broadcast_spec = re.findall(r"broadcast_all_(.+)", callback.data)[0]

    keyboard = InlineKeyboardBuilder()
    btn_cancel = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="back_to_main"
    )
    keyboard.row(btn_cancel)

    await callback.message.edit_text(
        "[1/2] Пришлите мне текст сообщения, которое хотите отправить.",
        reply_markup=keyboard.as_markup()
    )
    await state.update_data(dict(broadcast_spec=broadcast_spec))
    await state.set_state(states.BroadcastStates.get_text)


async def broadcast_company_spec_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    broadcast_spec = re.findall(r"broadcast_company_(.+)", callback.data)[0]

    keyboard = InlineKeyboardBuilder()
    btn_cancel = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="back_to_main"
    )
    keyboard.row(btn_cancel)

    keyboard = InlineKeyboardBuilder()
    btn_cancel = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="back_to_main"
    )
    keyboard.row(btn_cancel)

    await callback.message.edit_text(
        text="Теперь укажите ключевое слово салона, которое указано в названии ЛК YClients. "
             "Например: Менделеевская, Проспект Мира",
        reply_markup=keyboard.as_markup()
    )

    await state.update_data(dict(broadcast_spec=broadcast_spec))
    await state.set_state(states.BroadcastStates.get_company_id)


async def get_text_handler(message: Message, state: FSMContext):
    state_data = await state.get_data()
    broadcast_spec: str = state_data.get("broadcast_spec")

    photo = types.FSInputFile(f"bot/data/images/{broadcast_spec}.jpg")
    send_message = await message.answer_photo(
        photo=photo,
        caption=message.html_text
    )
    keyboard = InlineKeyboardBuilder()
    btn_start = InlineKeyboardButton(
        text="Запустить", callback_data="run_broadcast"
    )
    btn_cancel = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="back_to_main"
    )
    keyboard.row(btn_start)
    keyboard.row(btn_cancel)

    await message.answer(
        "[2/2] Запустить расссылку?",
        reply_markup=keyboard.as_markup(),
    )
    await state.update_data(dict(message=send_message))
    await state.set_state(states.BroadcastStates.broadcast)


async def broadcast_company_id_handler(callback: CallbackQuery, state: FSMContext, session):
    await callback.answer()
    state_data = await state.get_data()
    broadcast_spec: str = state_data.get("broadcast_spec")

    keyboard = InlineKeyboardBuilder()
    btn_cancel = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="back_to_main"
    )
    keyboard.row(btn_cancel)

    company_id = re.findall(r"broadcast_company_(\d+)", callback.data)
    if company_id:
        await state.update_data(dict(
            company_id=company_id[0]
        ))
    else:
        await state.update_data(dict(
            company_id=company_id
        ))

    if broadcast_spec:
        await callback.message.edit_text(
            "[1/2] Пришлите мне текст сообщения, которое хотите отправить.",
            reply_markup=keyboard.as_markup()
        )
        await state.set_state(states.BroadcastStates.get_text)
    else:
        await callback.message.edit_text(
            "[1/2] Пришлите сюда сообщение, которое хотите отправить ✉️\n\n"
            "<i>При необходимости добавления кнопок — воспользуйтесь сервисом @posted</i>",
            reply_markup=keyboard.as_markup()
        )

        await state.set_state(states.BroadcastStates.get_msg)


async def broadcast_company_all_handler(callback: CallbackQuery, state: FSMContext, session):
    await callback.answer()
    keyboard = InlineKeyboardBuilder()
    btn_cancel = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="back_to_main"
    )
    keyboard.row(btn_cancel)

    await callback.message.edit_text(
        text="Теперь укажите ключевое слово салона, которое указано в названии ЛК YClients. "
             "Например: Менделеевская, Проспект Мира",
        reply_markup=keyboard.as_markup()
    )

    await state.set_state(states.BroadcastStates.get_company_id)


async def get_company_id_handler(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    broadcast_spec: str = state_data.get("broadcast_spec")
    await state.clear()
    await state.update_data(dict(broadcast_spec=broadcast_spec))
    keyboard = InlineKeyboardBuilder()
    btn_cancel = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="back_to_main"
    )
    keyboard.row(btn_cancel)

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
            text="Не нашли такой салон.",
            reply_markup=keyboard.as_markup()
        )

    keyboard = InlineKeyboardBuilder()
    btn = InlineKeyboardButton(
        text=f"Рассылка {company['title']}",
        callback_data=f"broadcast_company_{company['id']}"
    )
    keyboard.row(btn)
    btn_cancel = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="back_to_main"
    )
    keyboard.row(btn_cancel)
    await message.answer(
        text=f"Для запуска рассылки в {company['title']} нажмите кнопку ниже.",
        reply_markup=keyboard.as_markup()
    )


async def get_msg_handler(message: types.Message, state: FSMContext):
    broadcaster = BaseBroadcaster(
        chats_id=[message.from_user.id],
        message=message,
        disable_web_page_preview=True
    )

    await broadcaster.run()

    keyboard = InlineKeyboardBuilder()
    btn_start = InlineKeyboardButton(
        text="Запустить", callback_data="run_broadcast"
    )
    btn_cancel = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="back_to_main"
    )
    keyboard.row(btn_start)
    keyboard.row(btn_cancel)

    await message.answer(
        "[2/2] Запустить расссылку?",
        reply_markup=keyboard.as_markup(),
    )
    await state.update_data(dict(message=message))
    await state.set_state(states.BroadcastStates.broadcast)


async def run_broadcast_handler(callback: types.CallbackQuery, state: FSMContext, session):
    state_data = await state.get_data()
    message: types.Message = state_data.get("message")
    company_id = state_data.get("company_id")

    await state.clear()
    await callback.answer()
    await callback.message.delete()

    keyboard = InlineKeyboardBuilder()
    btn_cancel = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="back_to_main"
    )
    keyboard.row(btn_cancel)

    company_name = "СЕТЬ"
    async with session() as open_session:
        if company_id:
            users: typing.List[int] = await open_session.execute(
                select(models.sql.User.id).filter_by(company_id=int(company_id))
            )
            users = users.scalars().all()
            response = await yclients.get_company(company_id)
            company_name = response["data"]["title"]
        else:
            users: typing.List[int] = await open_session.execute(select(models.sql.User.id))
            users = users.scalars().all()

    users = set(users)
    await callback.message.answer(
        text=f"Рассылка запущена в <b>{company_name}</b>. Кол-во пользователей: {len(users)}",
        reply_markup=keyboard.as_markup(),
        parse_mode="HTML"
    )

    broadcaster = BaseBroadcaster(chats_id=users, message=message)
    success_count = await broadcaster.run()
    await callback.message.answer(
        "Рассылка завершилась в <b>{}</b>.\n"
        "Отправлено сообщений: {} / {}".format(company_name, success_count, len(users)),
        parse_mode="HTML"
    )


def setup(dp: Dispatcher):
    dp.callback_query.register(
        broadcast_all_handler, F.data == "broadcast_all",
    )
    dp.callback_query.register(
        broadcast_all_spec_handler,
        F.data.in_({"broadcast_all_combo", "broadcast_all_new_service", "broadcast_all_new_company"})
    )
    dp.callback_query.register(
        broadcast_company_spec_handler,
        F.data.in_({"broadcast_company_combo", "broadcast_company_new_service", "broadcast_company_new_company"})
    )
    dp.callback_query.register(
        broadcast_all_all_handler, F.data == "broadcast_all_all",
    )
    dp.callback_query.register(
        broadcast_company_handler, F.data == "broadcast_company",
    )
    dp.callback_query.register(
        broadcast_company_all_handler, F.data == "broadcast_company_all",
    )
    dp.callback_query.register(
        broadcast_company_id_handler, F.data.regexp(r"broadcast_company_(\d+)"),
    )
    dp.message.register(
        get_company_id_handler,
        states.BroadcastStates.get_company_id,
    )
    dp.message.register(
        get_text_handler,
        states.BroadcastStates.get_text,
    )
    dp.message.register(
        get_msg_handler,
        states.BroadcastStates.get_msg,
    )
    dp.callback_query.register(
        run_broadcast_handler,
        states.BroadcastStates.broadcast,
    )
