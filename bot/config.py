from environs import Env
import os

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
BOT_ADMINS = env.list("BOT_ADMINS", subcast=int)
THROTTLE_RATE = env.float("THROTTLE_RATE")

POSTGRESQL_HOST = env.str("POSTGRESQL_HOST")
POSTGRESQL_PORT = env.str("POSTGRESQL_PORT")
POSTGRESQL_USER = env.str("POSTGRESQL_USER")
POSTGRESQL_PASSWORD = env.str("POSTGRESQL_PASSWORD")
POSTGRESQL_DBNAME = env.str("POSTGRESQL_DBNAME")

YCLIENTS_BEARER = env.str("YCLIENTS_BEARER")
YCLIENTS_USER = env.str("YCLIENTS_USER")

DIRNAME = os.path.dirname(__file__)
os.chdir(f"{DIRNAME}//..")

EMOJI_NUMS = [
    "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣",
]

MONTHS = {
    1: "января",
    2: "февраля",
    3: "марта",
    4: "апреля",
    5: "мая",
    6: "июня",
    7: "июля",
    8: "августа",
    9: "сентября",
    10: "октября",
    11: "ноября",
    12: "декабря"
}


YCLIENTS_HEADERS = {
    "Authorization": f"Bearer {YCLIENTS_BEARER}, User {YCLIENTS_USER}",
    "Content-Type":  "application/json",
    "Accept": "application/vnd.api.v2+json"
}