from aiogram.fsm.state import State, StatesGroup


class DeleteAdminStates(StatesGroup):
    get_admin_id = State()

