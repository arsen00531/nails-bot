from aiogram.fsm.state import StatesGroup, State


class FindSalonStates(StatesGroup):
    get_data = State()

