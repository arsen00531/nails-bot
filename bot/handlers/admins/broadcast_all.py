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
        text="Новая студия",
        callback_data="broadcast_all_new_company"
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


async def broadcast_all_all_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    keyboard = InlineKeyboardBuilder()
    btn_cancel = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="admin_panel"
    )
    keyboard.row(btn_cancel)

    await callback.message.edit_text(
        "[1/2] Пришлите сюда сообщение, которое хотите отправить ✉️\n\n"
        "<i>При необходимости добавления кнопок — воспользуйтесь сервисом @posted</i>",
        reply_markup=keyboard.as_markup()
    )
    await state.set_state(states.BroadcastStates.get_button)


async def broadcast_all_spec_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    broadcast_spec = re.findall(r"broadcast_all_(.+)", callback.data)[0]

    keyboard = InlineKeyboardBuilder()
    btn_cancel = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="admin_panel"
    )
    keyboard.row(btn_cancel)

    await callback.message.edit_text(
        "[1/2] Пришлите сюда сообщение, которое хотите отправить ✉️\n\n"
        "<i>Учтите, что к сообщению нельзя добавить кнопки и фотографии. "
        "При необходимости добавления кнопок — создайте рассылку категории "
        "«Общая» и воспользуйтесь сервисом @posted</i>",
        reply_markup=keyboard.as_markup()
    )
    await state.update_data(dict(broadcast_spec=broadcast_spec))
    await state.set_state(states.BroadcastStates.get_text)


def setup(dp: Dispatcher):
    dp.callback_query.register(
        broadcast_all_handler, F.data == "broadcast_all",
    )

    dp.callback_query.register(
        broadcast_all_spec_handler,
        F.data.in_({"broadcast_all_combo", "broadcast_all_new_service", "broadcast_all_new_company"})
    )

    dp.callback_query.register(
        broadcast_all_all_handler, F.data == "broadcast_all_all",
    )
