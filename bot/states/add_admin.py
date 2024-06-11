from aiogram.fsm.state import State, StatesGroup


class AddAdminStates(StatesGroup):
    get_admin_id = State()

