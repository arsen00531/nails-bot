from .is_bot_admin import IsBotAdminFilter
from .rate_limit import RateLimitFilter
from aiogram import Dispatcher


def setup(dp: Dispatcher):
    dp.message.filter(IsBotAdminFilter)
    dp.message.filter(RateLimitFilter)
    dp.callback_query.filter(IsBotAdminFilter)
