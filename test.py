# import json
#
# import requests
#
#
# from geopy.geocoders import Nominatim #Подключаем библиотеку
# geolocator = Nominatim(user_agent="Tester") #Указываем название приложения (так нужно, да)
# adress = str(input('Введите адрес: \n')) #Получаем интересующий нас адрес
# location = geolocator.geocode(adress) #Создаем переменную, которая состоит из нужного нам адреса
# print(location) #Выводим результат: адрес в полном виде
# print(location.latitude, location.longitude) #И теперь выводим GPS-координаты нужного нам адреса

import requests
# r = requests.get("https://api.yclients.com/api/v1/companies?my=1&showBookforms=1", headers=headers)
#
# salons: list = r.json()["data"]
# salon_1 = salons[0]
# print(salon_1)


# r = requests.get(f"https://api.yclients.com/api/v1/company/{salon_1}?showBookforms=1", headers=headers)
# print(r.json()["data"])
# titles = [i["title"] for i in salons]
# addresses = [i["address"] for i in salons]
# print(titles, addresses)

#
# import emoji
#
# emojis = [emoji.emojize(f'{i}\uFE0F\u20E3') for i in range(1, 13)]  # Создаем список с эмодзи от 1️⃣ до 🔟
#
# emoji_dict = {emoji: index for index, emoji in enumerate(emojis)}  # Создаем словарь с ключами, где ключ - эмодзи, а значение - индекс
#
# print(emoji_dict)
#
# pressed_emoji = "11️⃣"  # Получаем эмодзи при нажатии кнопки
# index = emoji_dict.get(pressed_emoji)  # Получаем соответствующий индекс из словаря
#
# # print(index)
#
# print(len("2️⃣"))
# print("2️⃣2️⃣"[:3])
# print("2️⃣"[:2])
from datetime import datetime

#
# r = requests.get(f"https://yclients.com/c/6hReb/SJFsJ/")
# print(r.url)
#
#
# record_datetime = "08.07 10:00"
# datetime_now = "08.07 9:50"
# last_notification = None
# target_datetime = "00:30"
#
# "record_datetime - datetime_now = 7:00"
#
# last_notification = "08.07 6:00"
# (record_datetime - last_notification) >= target_datetime


