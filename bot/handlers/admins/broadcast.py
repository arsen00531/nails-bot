import enum
import re

from aiogram.fsm.context import FSMContext
from aiogram import types, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from bot import keyboards
import typing
from bot import states
from bot import models, filters
from bot.services.broadcaster import BaseBroadcaster
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from sqlalchemy import select
import validators


class UserGroups(enum.Enum):
    ALL = "all"
    COMPLETED = "completed"
    NOT_COMPLETED = "not_completed"


async def broadcast_cmd_handler(message: Message, state: FSMContext):
    keyboard = InlineKeyboardBuilder()
    btn_1 = InlineKeyboardButton(
        text=UserGroups.ALL.value.capitalize(),
        callback_data=UserGroups.ALL.value
    )
    btn_2 = InlineKeyboardButton(
        text=UserGroups.COMPLETED.value.capitalize(),
        callback_data=UserGroups.COMPLETED.value
    )
    btn_3 = InlineKeyboardButton(
        text=UserGroups.NOT_COMPLETED.value.replace("_", " ").capitalize(),
        callback_data=UserGroups.NOT_COMPLETED.value
    )
    keyboard.row(btn_1)
    keyboard.row(btn_2)
    keyboard.row(btn_3)

    await message.answer(
        "[1/3] Select group users:",
        reply_markup=keyboard.as_markup()
    )
    await state.set_state(states.BroadcastStates.set_user_group)


async def set_user_group(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete_reply_markup()
    await state.update_data(user_group=callback.data)
    if callback.data in (UserGroups.COMPLETED.value, UserGroups.NOT_COMPLETED.value):
        await callback.message.answer(text="[1.5/3] Send me campaign for url:")
        await state.set_state(states.BroadcastStates.get_campaign_url)
    else:
        await callback.message.answer(text="[2/3] Send me message for broadcast:")
        await state.set_state(states.BroadcastStates.pre_broadcast)


async def get_campaign_url(message: types.Message, state: FSMContext, session):
    # https://t.me/RaiseAnon_bot/campaign?startapp=54bbfa17efe2ccad
    campaign_url = message.text

    if not validators.url(campaign_url):
        return await message.answer(
            text="Not valid url.\n\n"
                 "/cancel - for exit."
        )

    campaign_id = re.findall("startapp=(.+)", campaign_url)[0]
    await state.update_data(campaign_id=campaign_id)
    await message.answer(text="[2/3] Send me message for broadcast:")
    await state.set_state(states.BroadcastStates.pre_broadcast)


async def getting_msg(message: types.Message, state: FSMContext):
    broadcaster = BaseBroadcaster(
        chats_id=[message.from_user.id],
        message=message,
        disable_web_page_preview=True
    )

    await broadcaster.run()

    keyboard = InlineKeyboardBuilder()
    btn_start = InlineKeyboardButton(
        text="Run", callback_data="accept"
    )
    btn_cancel = InlineKeyboardButton(
        text="Cancel", callback_data="cancel"
    )
    keyboard.row(btn_start)
    keyboard.row(btn_cancel)

    await message.answer(
        "[3/3] Run broadcast?",
        reply_markup=keyboard.as_markup(),
    )
    await state.update_data(dict(message=message))
    await state.set_state(states.BroadcastStates.broadcast)


async def start_broadcast(callback: types.CallbackQuery, state: FSMContext, session):
    state_data = await state.get_data()
    message: types.Message = state_data.get("message")
    user_group = state_data.get("user_group")
    campaign_id = state_data.get("campaign_id")

    await state.clear()
    await callback.answer()

    if callback.data == "cancel":
        return await callback.message.answer("Cancel broadcast.")

    if user_group == UserGroups.ALL.value:
        async with session() as open_session:
            users: typing.List[int] = await open_session.execute(select(models.sql.User.id))
            users = users.scalars().all()

    elif user_group == UserGroups.COMPLETED.value:

        async with session() as open_session:
            users: typing.List[int] = await open_session.execute(
                select(models.sql.DoneCampaign.user_id).filter_by(campaign_id=campaign_id))
            users = users.scalars().all()

    elif user_group == UserGroups.NOT_COMPLETED.value:
        async with session() as open_session:
            done_users: typing.List[int] = await open_session.execute(
                select(models.sql.DoneCampaign.user_id).filter_by(campaign_id=campaign_id))
            done_users = set(done_users.scalars().all())

            all_users: typing.List[int] = await open_session.execute(select(models.sql.User.id))
            all_users = set(all_users.scalars().all())
            users = all_users.difference(done_users)

    users = set(users)

    await callback.message.answer(f"Broadcast is run. Users count: {len(users)}")

    broadcaster = BaseBroadcaster(chats_id=users, message=message)
    success_count = await broadcaster.run()
    await callback.message.answer(
        "Success broadcast.\n"
        "Send messages: {} / {}".format(success_count, len(users))
    )


def setup(dp: Dispatcher):
    dp.message.register(
        broadcast_cmd_handler, Command("broadcast"),
    )
    dp.callback_query.register(
        set_user_group,
        states.BroadcastStates.set_user_group,
    )
    dp.message.register(
        get_campaign_url,
        states.BroadcastStates.get_campaign_url
    )
    dp.message.register(
        getting_msg,
        states.BroadcastStates.pre_broadcast,
    )
    dp.callback_query.register(
        start_broadcast,
        states.BroadcastStates.broadcast,
    )
