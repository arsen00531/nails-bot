from aiogram.fsm.state import StatesGroup, State


class BroadcastStates(StatesGroup):
    get_msg = State()
    get_text = State()
    broadcast = State()
    get_company_id = State()