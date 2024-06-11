from aiogram.fsm.state import StatesGroup, State


class BroadcastStates(StatesGroup):
    set_user_group = State()
    get_campaign_url = State()
    pre_broadcast = State()
    broadcast = State()
