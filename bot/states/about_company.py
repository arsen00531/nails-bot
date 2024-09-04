from aiogram.fsm.state import State, StatesGroup


class AboutCompanyStates(StatesGroup):
    get_company_id = State()
    get_url = State()

