from aiogram.types import Message
from aiogram.exceptions import TelegramRetryAfter
import asyncio
import logging
import typing
from bot.services.sender import CopySender


class BaseBroadcaster:
    def __init__(self, chats_id: typing.List[int], message: Message, *args, **kwargs):
        self.chats_id = chats_id
        self.message = message
        self.args = args
        self.kwargs = kwargs

    async def _send(self, chat_id: int):
        try:
            await CopySender(self.message).send_copy(chat_id=chat_id, *self.args, **self.kwargs)
        except TelegramRetryAfter as e:
            logging.error(f"Target [ID:{chat_id}]: Flood limit is exceeded. Sleep {e.retry_after} seconds.")
            await asyncio.sleep(e.retry_after)
            await self.message.send_copy(chat_id=chat_id, *self.args, **self.kwargs)
        except Exception as e:
            logging.error(e)
            logging.exception(f"Target [ID:{chat_id}]: failed")
        else:
            logging.info(f"Target [ID:{chat_id}]: success")
            return True
        return False

    async def run(self) -> int:
        count = 0
        try:
            for chat_id in self.chats_id:
                if await self._send(chat_id):
                    count += 1
                await asyncio.sleep(.05)
        finally:
            logging.info(f"{count} messages successful sent.")

        return count
