from aiogram import Dispatcher
from . import start
from . import record
from . import nearest_salon
from . import auth
from . import get_client_records
from . import client_record
from . import find_salon
from . import back_reply
from . import delete_record
from . import support_message

def setup(dp: Dispatcher):
    for module in (
            start, record, nearest_salon, auth, get_client_records, client_record, find_salon,
            back_reply, delete_record, support_message
    ):
        module.setup(dp)
