import re
from aiogram.fsm.context import FSMContext
from aiogram import types, Dispatcher, F
from aiogram.types import CallbackQuery, Message
from bot import states
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from bot.services import yclients


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
        text="Новая студия",
        callback_data="broadcast_company_new_company"
    )
    keyboard.row(btn_3, btn_4)
    btn_cancel = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="admin_panel"
    )
    keyboard.row(btn_cancel)

    await callback.message.edit_text(
        "Выберите необходимую категорию рассылки ниже 👇",
        reply_markup=keyboard.as_markup()
    )


async def broadcast_company_spec_handler(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    company_id = state_data.get("company_id")
    await callback.answer()

    broadcast_spec = re.findall(r"broadcast_company_(.+)", callback.data)[0]

    keyboard = InlineKeyboardBuilder()
    btn_cancel = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="admin_panel"
    )
    keyboard.row(btn_cancel)

    await state.update_data(dict(broadcast_spec=broadcast_spec))

    if company_id:
        await callback.message.edit_text(
            "[1/2] Пришлите сюда сообщение, которое хотите отправить ✉️\n\n"
            "<i>Учтите, что к сообщению нельзя добавить кнопки и фотографии. "
            "При необходимости добавления кнопок — создайте рассылку категории "
            "«Общая» и воспользуйтесь сервисом @posted</i>",
            reply_markup=keyboard.as_markup()
        )
        await state.set_state(states.BroadcastStates.get_text)
    else:
        await callback.message.edit_text(
            text="Теперь укажите ключевое слово студии, которое указано в названии ЛК YClients. "
                 "Например: Менделеевская, Проспект Мира",
            reply_markup=keyboard.as_markup()
        )

        await state.set_state(states.BroadcastStates.get_company_id)


async def broadcast_company_all_handler(callback: CallbackQuery, state: FSMContext, session):
    state_data = await state.get_data()
    company_id = state_data.get("company_id")

    await callback.answer()
    keyboard = InlineKeyboardBuilder()
    btn_cancel = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="admin_panel"
    )
    keyboard.row(btn_cancel)

    if company_id:
        await callback.message.edit_text(
            "[1/2] Пришлите сюда сообщение, которое хотите отправить ✉️\n\n"
            "<i>При необходимости добавления кнопок — воспользуйтесь сервисом @posted</i>",
            reply_markup=keyboard.as_markup()
        )
        await state.set_state(states.BroadcastStates.get_msg)
    else:
        await callback.message.edit_text(
            text="Теперь укажите ключевое слово студии, которое указано в названии ЛК YClients. "
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
        callback_data="admin_panel"
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
            text="Не нашли такую студию.",
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
        callback_data="admin_panel"
    )
    keyboard.row(btn_cancel)
    await message.answer(
        text=f"Для запуска рассылки в {company['title']} нажмите кнопку ниже.",
        reply_markup=keyboard.as_markup()
    )


async def broadcast_company_id_handler(callback: CallbackQuery, state: FSMContext, session):
    await callback.answer()
    state_data = await state.get_data()
    broadcast_spec: str = state_data.get("broadcast_spec")

    keyboard = InlineKeyboardBuilder()
    btn_cancel = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="admin_panel"
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
            "[1/2] Пришлите сюда сообщение, которое хотите отправить ✉️\n\n"
            "<i>Учтите, что к сообщению нельзя добавить кнопки и фотографии. "
            "При необходимости добавления кнопок — создайте рассылку категории "
            "«Общая» и воспользуйтесь сервисом @posted</i>",
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



def setup(dp: Dispatcher):
    dp.callback_query.register(
        broadcast_company_handler, F.data == "broadcast_company",
                                   )
    dp.callback_query.register(
        broadcast_company_spec_handler,
        F.data.in_({"broadcast_company_combo", "broadcast_company_new_service", "broadcast_company_new_company"})
    )

    dp.callback_query.register(
        broadcast_company_all_handler, F.data == "broadcast_company_all",
    )

    dp.message.register(
        get_company_id_handler,
        states.BroadcastStates.get_company_id,
    )

    dp.callback_query.register(
        broadcast_company_id_handler, F.data.regexp(r"broadcast_company_(\d+)"),
    )
