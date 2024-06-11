from aiogram import Dispatcher
from . import start
from . import record


def setup(dp: Dispatcher):
    for module in (
            start, record
    ):
        module.setup(dp)
