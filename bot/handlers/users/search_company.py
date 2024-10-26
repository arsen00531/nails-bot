from aiogram import types, Dispatcher
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from aiogram import F
from aiogram.fsm.context import FSMContext
from bot.states import FindCompanyStates
from bot.services import yclients
from sqlalchemy import select, insert
from bot import models
from bot import config
from fuzzywuzzy import process, fuzz
import re
import math
import requests

# Функция для расчета расстояния между двумя точками на поверхности Земли (широта, долгота)
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Радиус Земли в километрах

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

def find_two_nearest_stations(user_lat, user_lon, companies):
    # Считаем расстояния до всех станций
    stations_with_distance = []
    for company in companies:
        station_lat = company["coordinate_lat"]
        station_lon = company["coordinate_lon"]
        distance = haversine(user_lat, user_lon, station_lat, station_lon)
        stations_with_distance.append((company, distance))

    # Сортируем станции по расстоянию (от ближайших к дальним)
    stations_with_distance.sort(key=lambda x: x[1])

    # Возвращаем две ближайшие станции
    return stations_with_distance[:2]

# Функция для отправки запроса к Yandex Geocoder API и получения координат
def get_coordinates(address, api_key):
    url = f"https://geocode-maps.yandex.ru/1.x/?apikey={api_key}&geocode={address}&format=json"
    response = requests.get(url)
    
    if response.status_code == 200:
        json_data = response.json()
        pos = json_data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
        name = json_data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['name'].split(' ')[1]
        lon, lat = map(float, pos.split())
        return lat, lon, name
    else:
        raise Exception("Ошибка при запросе к Yandex Geocoder API")

# Функция для получения координат всех станций метро из списка stations
def get_stations_coordinates(stations, api_key):
    stations_with_coordinates = []

    for station in stations:
        try:
            lat, lon = get_coordinates(station["title"], api_key)  # Получаем координаты станции
            station["lat"] = lat
            station["lon"] = lon
            stations_with_coordinates.append(station)
        except Exception as e:
            print(f"Ошибка получения координат для станции {station['title']}: {e}")

    return stations_with_coordinates

async def search_company_handler(message: types.Message, state: FSMContext):
    keyboard = InlineKeyboardBuilder()
    btn = InlineKeyboardButton(
        text="Выход",
        callback_data="back_to_main"
    )
    keyboard.row(btn)

    await message.answer(
        text="Отправьте <b>станцию метро</b>\n"
             "<i>(например: Менделеевская)</i>\n\n"
             "Или <b>название улицы</b> студии\n"
             "<i>(например: Тверская-Ямская)</i>",
        reply_markup=keyboard.as_markup()
    )
    await state.set_state(FindCompanyStates.get_data)


async def get_data_handler(message: types.Message, state: FSMContext, session):
    await state.clear()
    response = await yclients.get_companies()
    companies = response["data"]

    company_titles = [i["title"].split('City Nails ')[1] for i in companies if len(i["title"].split('City Nails ')) == 2]
    company_addresses = [i["address"] for i in companies]

    # Пытаемся найти студию по нечёткому совпадению с названием или адресом
    title_match = process.extractOne(message.text, company_titles, scorer=fuzz.token_sort_ratio)
    address_match = process.extractOne(message.text, company_addresses, scorer=fuzz.token_sort_ratio)

    print(title_match, address_match, address_match[1])

    if title_match and title_match[1] >= 75:
        company = next(i for i in companies if i["title"].split('City Nails ')[1] == title_match[0] if len(i["title"].split('City Nails ')) == 2)
    elif address_match and address_match[1] >= 75:
        company = next(i for i in companies if i["address"] == address_match[0])
    else:
        async with session() as open_session:
            stations = await open_session.execute(select(models.sql.Station))
            stations: list[models.sql.Station] = stations.scalars().all()

        station_titles = [station.title for station in stations]

        title_match = process.extractOne(message.text, station_titles, scorer=fuzz.token_sort_ratio)

        nearest_companies = []
        
        if title_match and title_match[1] >= 75:
            for station in stations:
                if station.title == title_match[0]:
                    user_lat, user_lon = station.coordinate_lat, station.coordinate_lon
                    nearest_companies = find_two_nearest_stations(float(user_lat), float(user_lon), companies)
        else:
            user_lat, user_lon, name = get_coordinates(message.text, config.YANDEX_GEOKODER_API)
            nearest_companies = find_two_nearest_stations(user_lat, user_lon, companies)
            st = models.sql.Station()
            st.coordinate_lat = str(user_lat)
            st.coordinate_lon = str(user_lon)
            st.title = name
            async with session() as open_session:
                open_session.add(st)
                await open_session.commit()
        for i in range(len(nearest_companies)):
            print(f"Ближайшая станция метро: {nearest_companies[i][0]['title']}")

        keyboard = InlineKeyboardBuilder()
        for company in nearest_companies:
            company_title = company[0]["title"]
            company_id = company[0]["id"]
            
            btn = InlineKeyboardButton(
                text=f"{company_title}",
                callback_data=f"near_company_{company_id}"
            )
            keyboard.row(btn)
        btn = InlineKeyboardButton(
            text="◀️ Назад",
            callback_data="back_to_main"
        )
        keyboard.row(btn)
        photo = types.FSInputFile("bot/data/images/nearest_company.jpg")
        return await message.answer_photo(
            photo=photo,
            caption="К сожалению, в указанной вами локации пока нет нашей студии 😔\nНо вот два ближайших филиала City Nails, где вы можете записаться на процедуры!",
            reply_markup=keyboard.as_markup()
        )

    keyboard = InlineKeyboardBuilder()

    btn_1 = InlineKeyboardButton(
        text="Написать администратору 📩",
        callback_data=f"chat_answer_to_{company['id']}"
    )
    keyboard.row(btn_1)

    async with session() as open_session:
        about_company = await open_session.execute(
            select(models.sql.AboutCompany).filter_by(company_id=int(company['id'])))
        about_company: models.sql.AboutCompany = about_company.scalars().first()

    if about_company:
        web_app_info = types.WebAppInfo(url=about_company.url)
        btn_2 = InlineKeyboardButton(
            text="Подробнее",
            web_app=web_app_info
        )
    else:
        web_app_info = types.WebAppInfo(url="https://citynails.studio/")
        btn_2 = InlineKeyboardButton(
            text="Подробнее",
            web_app=web_app_info
        )

    web_app_info = types.WebAppInfo(url=company["bookforms"][0]["url"])
    btn_3 = InlineKeyboardButton(
        text="Записаться",
        web_app=web_app_info
    )
    keyboard.row(btn_2, btn_3)

    btn = InlineKeyboardButton(
        text="Выход",
        callback_data="back_to_main"
    )
    keyboard.row(btn)

    await message.answer_venue(
        title=company["title"],
        address=company["address"],
        latitude=company["coordinate_lat"],
        longitude=company["coordinate_lon"],
        reply_markup=keyboard.as_markup()
    )


def setup(dp: Dispatcher):
    dp.message.register(search_company_handler, F.text == "Поиск 🔎")
    dp.message.register(get_data_handler, FindCompanyStates.get_data)
