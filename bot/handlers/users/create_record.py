from aiogram import types, Dispatcher
from aiogram import F
import tools

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
    msg_text = await tools.filer.read_txt("create_record")
    photo = types.FSInputFile("bot/data/images/create_record.jpg")
    await message.answer_photo(
        photo=photo,
        caption=msg_text,
        reply_markup=keyboard
    )


def setup(dp: Dispatcher):
    dp.message.register(create_record_handler, F.text == "Записаться 🟣")
