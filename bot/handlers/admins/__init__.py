from aiogram import Dispatcher
from . import add_admin
from . import stats
from . import cancel
from . import broadcast
from . import panel
from . import add_yandex_company
from . import broadcast_all
from . import broadcast_company


def setup(dp: Dispatcher):
    for module in (
            cancel, add_admin, stats, broadcast, panel, add_yandex_company,
            broadcast_all, broadcast_company
    ):
        module.setup(dp)
