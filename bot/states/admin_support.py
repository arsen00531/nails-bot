from aiogram.fsm.state import StatesGroup, State


class AdminSupportStates(StatesGroup):
    get_msg = State()
