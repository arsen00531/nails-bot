from aiogram import types, Dispatcher
from aiogram import F


async def create_record_handler(message: types.Message):
    buttons = [
        [
            types.KeyboardButton(text="Поиск 🔎"),
            types.KeyboardButton(text="Ближайший 📍", request_location=True),
        ],
        [
            types.KeyboardButton(text="◀️ Назад"),
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)

    await message.answer(
        text="Выберите:",
        reply_markup=keyboard
    )


def setup(dp: Dispatcher):
    dp.message.register(create_record_handler, F.text == "Записаться 🟣")
