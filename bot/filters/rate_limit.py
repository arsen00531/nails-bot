from aiogram.filters.base import Filter
from aiogram.types import Message
from cachetools import TTLCache


class RateLimitFilter(Filter):
    def __init__(self, ttl: int):
        self.cache_l1 = TTLCache(maxsize=10_000, ttl=ttl)

    async def __call__(self, context: Message) -> bool:
        if context.from_user.id in self.cache_l1:
            return False

        self.cache_l1[context.from_user.id] = None
        return True
