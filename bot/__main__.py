import asyncio
import logging

from aiogram import Bot, Dispatcher, types

from aiogram.fsm.storage.memory import MemoryStorage

from bot import middlewares, handlers, filters
from bot import config
from bot.services import commands_setter, admin_notificator, logger
import database
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bot.services.scheduler import notify_sender
from aiogram.client.default import DefaultBotProperties


async def main():
    db = database.implement.AsyncPostgreSQL(
        database_name=config.POSTGRESQL_DBNAME,
        username=config.POSTGRESQL_USER,
        password=config.POSTGRESQL_PASSWORD,
        hostname=config.POSTGRESQL_HOST,
        port=config.POSTGRESQL_PORT
    )

    session = await database.manager.create_async_session(db)

    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage, session=session)

    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        func=notify_sender,
        trigger="interval",
        seconds=30,
        args=[session, bot]
    )
    scheduler.start()

    filters.setup(dp)
    middlewares.setup(dp)
    handlers.setup(dp)

    await commands_setter.set_bot_commands(bot)
    await admin_notificator.notify(bot)

    try:
        await bot.delete_webhook(True)
        await dp.start_polling(bot)
    finally:
        await dp.storage.close()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot stopped!")
