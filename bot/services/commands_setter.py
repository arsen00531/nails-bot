from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat
from bot import config


async def set_bot_commands(bot: Bot):
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Start"),
        ]
    )

    for admin_id in config.BOT_ADMINS:
        await bot.set_my_commands(
            [
                BotCommand(command="start", description="Start"),
                BotCommand(command="broadcast", description="Broadcast"),
                BotCommand(command="stats", description="stats"),
                BotCommand(command="addadmin", description="Add new admin"),
                BotCommand(command="deleteadmin", description="Delete admin"),
            ],
            scope=BotCommandScopeChat(chat_id=admin_id)
        )
