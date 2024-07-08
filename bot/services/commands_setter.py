from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat
from bot import config


async def set_bot_commands(bot: Bot):
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Запустить"),
        ]
    )

    for admin_id in config.BOT_ADMINS:
        await bot.set_my_commands(
            [
                BotCommand(command="start", description="Запустить"),
                BotCommand(command="broadcast", description="Рассылка"),
                BotCommand(command="addadmin", description="Добавить админа"),
                BotCommand(command="deleteadmin", description="Удалить админа"),
            ],
            scope=BotCommandScopeChat(chat_id=admin_id)
        )
