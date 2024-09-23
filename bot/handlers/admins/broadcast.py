from aiogram.fsm.context import FSMContext
from aiogram import types, Dispatcher, F
from aiogram.types import Message, WebAppInfo, CallbackQuery
import typing
from bot import states
from bot import models, filters
from bot.services.broadcaster import BaseBroadcaster
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from sqlalchemy import select
from bot.services import yclients
from tools import table
from urllib.parse import urlparse
 

async def get_msg_handler(message: types.Message, state: FSMContext):
    textMessage = (await state.get_data())['get_button']
    last_message: Message = (await state.get_data())['get_button_message']
    parse = await parseButtons(message.text)

    if type(parse) is str:
        return await message.answer("Your message is invalid")
    
    buttons = parse[0]
    names = parse[1]
    company_names = parse[2]
    urls = parse[3]
    
    if last_message.photo:
        messageNew = await last_message.answer_photo(last_message.photo[-1].file_id, caption=textMessage, reply_markup=buttons)
    else:
        messageNew = await last_message.answer(text=textMessage, reply_markup=buttons)

    await messageNew.delete()

    broadcaster = BaseBroadcaster(
        chats_id=[message.from_user.id],
        message=messageNew,
        disable_web_page_preview=True
    )

    await broadcaster.run()
    
    keyboard = InlineKeyboardBuilder()
    btn_start = InlineKeyboardButton(
        text="Запустить", callback_data="run_broadcast"
    )
    btn_cancel = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="admin_panel"
    )
    keyboard.row(btn_start)
    keyboard.row(btn_cancel)

    await message.answer(
        "[2/2] Запустить расссылку?",
        reply_markup=keyboard.as_markup(),
    )
    await state.update_data(dict(message=messageNew))
    await state.update_data(buttons_name=names)
    await state.update_data(urls=urls)
    await state.update_data(company_names=company_names)
    await state.set_state(states.BroadcastStates.broadcast)


async def get_text_handler(message: Message, state: FSMContext):
    state_data = await state.get_data()
    broadcast_spec: str = state_data.get("broadcast_spec")

    photo = types.FSInputFile(f"bot/data/images/{broadcast_spec}.jpg")
    send_message = await message.answer_photo(
        photo=photo,
        caption=message.html_text
    )
    keyboard = InlineKeyboardBuilder()
    btn_start = InlineKeyboardButton(
        text="Запустить", callback_data="run_broadcast"
    )
    btn_cancel = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="admin_panel"
    )
    keyboard.row(btn_start)
    keyboard.row(btn_cancel)

    await message.answer(
        "[2/2] Запустить расссылку?",
        reply_markup=keyboard.as_markup(),
    )
    await state.update_data(dict(message=send_message))

async def run_broadcast_handler(callback: types.CallbackQuery, state: FSMContext, session):
    state_data = await state.get_data()
    message: types.Message = state_data.get("message")
    buttons_name = state_data.get('buttons_name')
    company_names = state_data.get('company_names')
    urls = state_data.get('urls')
    company_id = state_data.get("company_id")

    await state.clear()
    await callback.answer()
    await callback.message.delete()


    keyboard = InlineKeyboardBuilder()
    btn_cancel = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="admin_panel"
    )
    keyboard.row(btn_cancel)

    validNames = table.checkTable(buttons_name)
    if not(validNames):
        return await callback.message.answer(
            text=f"Рассылка не запущена, так как такое название рассылки уже существует",
            reply_markup=keyboard.as_markup(),
            parse_mode="HTML"
        )

    company_name = "СЕТЬ"
    async with session() as open_session:
        if company_id:
            users: typing.List[int] = await open_session.execute(
                select(models.sql.User.id).filter_by(company_id=int(company_id))
            )
            users = users.scalars().all()
            response = await yclients.get_company(company_id)
            company_name = response["data"]["title"]
        else:
            users: typing.List[int] = await open_session.execute(select(models.sql.User.id))
            users = users.scalars().all()

    users = set(users)
    await callback.message.answer(
        text=f"Рассылка запущена в <b>{company_name}</b>. Кол-во пользователей: {len(users)}",
        reply_markup=keyboard.as_markup(),
        parse_mode="HTML"
    )

    broadcaster = BaseBroadcaster(chats_id=users, message=message)
    success_count = await broadcaster.run()
    await callback.message.answer(
        "Рассылка завершилась в <b>{}</b>.\n"
        "Отправлено сообщений: {} / {}".format(company_name, success_count, len(users)),
        parse_mode="HTML"
    )

    for i in range(len(buttons_name)):
        table.addTableLink(buttons_name[i], urls[i], company_names[i], True)

async def get_button_handler(message: types.Message, state: FSMContext):
    keyboard = InlineKeyboardBuilder()
    btn_skip = InlineKeyboardButton(
        text="Пропустить", 
        callback_data="skip_button"
    )
    btn_cancel = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="admin_panel"
    )
    keyboard.row(btn_skip)
    keyboard.row(btn_cancel)

    last_message = message

    await message.answer(
        "URL-КНОПКИ \n"
        "Отправьте боту список URL-кнопок и их названия в следующем формате: \n\n"
        "Кнопка 1 - http://link.com - name1\nКнопка 2 - http://link.com - name2\n\n"
        'Используйте разделитель " | ", чтобы добавить до 8 кнопок в один ряд (допустимо 15 рядов):\n\n'
        "Кнопка 1 - http://link.com - name1 | Кнопка 2 - http://link.com - name2\n"
        "Либо нажмите пропустить",
        reply_markup=keyboard.as_markup(),
    )
    text = message.caption if message.photo else message.text
    await state.update_data(dict(message=message))
    await state.update_data(get_button_message=last_message)
    await state.update_data(get_button=text)
    await state.set_state(states.BroadcastStates.get_msg) 

async def skip_button_handler(callback: CallbackQuery, state: FSMContext):
    callback.answer()
    last_message: Message = (await state.get_data())['get_button_message']

    broadcaster = BaseBroadcaster(
        chats_id=[last_message.from_user.id],
        message=last_message,
        disable_web_page_preview=True
    )

    await broadcaster.run()
    
    keyboard = InlineKeyboardBuilder()
    btn_start = InlineKeyboardButton(
        text="Запустить", callback_data="run_broadcast"
    )
    btn_cancel = InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="admin_panel"
    )
    keyboard.row(btn_start)
    keyboard.row(btn_cancel)

    await last_message.answer(
        "[2/2] Запустить расссылку?",
        reply_markup=keyboard.as_markup(),
    )
    await state.update_data(dict(message=last_message))
    await state.set_state(states.BroadcastStates.broadcast)

async def web_app_message_handler(message: types.Message):
    print('lox')
    data = message.web_app_data.data
    await message.answer(f"Получены данные из Web App: {data}")

async def parseButtons(message: str):
    if not(message):
        return
    if len(message) == 0:
        return
    
    keyboard = InlineKeyboardBuilder()
    names = []
    company_names = []
    urls = []
    for link in message.split('|'):
        spl = link.split('-')
        if len(spl) != 3:
            return "link or name are invalid"
        else:
            button_name = spl[0]
            url = spl[1].replace(' ', '')
            name = spl[2]
            if len(button_name) == 0:
                return 'text button is invalid'
            if not(is_valid_url(url)):
                return 'link is invalid'
            if len(name) == 0:
                return 'name button is invalid'
            names.append(name)

            btn = InlineKeyboardButton(
                text=button_name,
                web_app=WebAppInfo(url="https://www.connectbirga.ru/nails"),
            )
            keyboard.row(btn)
            urls.append(url)

            if url.find('https://n812348.yclients.com/company/') != -1:
                url = url.replace('https://n812348.yclients.com/company/', '')
                url = url.split('/')
                company = await yclients.get_company(int(url[0]))
                company_names.append(company["data"]["public_title"].replace('City Nails ', ''))
            else:
                company_names.append('Другое')
    
    return keyboard.as_markup(), names, company_names, urls

def is_valid_url(url: str):
    parsed_url = urlparse(url)
    return bool(parsed_url.scheme and parsed_url.netloc)


def setup(dp: Dispatcher):
    dp.message.register(
        get_text_handler,
        states.BroadcastStates.get_text,
    )
    dp.message.register(
        get_msg_handler,
        states.BroadcastStates.get_msg,
    )
    dp.message.register(
        get_button_handler,
        states.BroadcastStates.get_button,
    )
    dp.callback_query.register(
        skip_button_handler,
        F.data == "skip_button",
    )
    dp.message.register(
        web_app_message_handler,
        F.web_app_data,
    )
    dp.callback_query.register(
        run_broadcast_handler,
        F.data == "run_broadcast",
    )
