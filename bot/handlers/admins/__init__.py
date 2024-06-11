from aiogram import Dispatcher
from . import add_admin
from . import stats
from . import cancel
from . import broadcast


def setup(dp: Dispatcher):
    for module in (
            cancel, add_admin, stats, broadcast
    ):
        module.setup(dp)
