from aiogram import Dispatcher
from . import start
from . import create_record
from . import nearest_company
from . import auth
from . import get_records
from . import get_record
from . import search_company
from . import back
from . import delete_record
from . import support


def setup(dp: Dispatcher):
    for module in (
            start, create_record, nearest_company, auth, get_records, get_record, search_company,
            back, delete_record, support
    ):
        module.setup(dp)
