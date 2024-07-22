from aiogram.fsm.state import StatesGroup, State


class FindCompanyStates(StatesGroup):
    get_data = State()

