from aiogram.fsm.state import State, StatesGroup


class YandexCompanyStates(StatesGroup):
    get_url = State()

