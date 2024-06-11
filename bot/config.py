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

APP_URL = env.str("APP_URL")

DIRNAME = os.path.dirname(__file__)
os.chdir(f"{DIRNAME}//..")
