import typing
from aiogram import types, Dispatcher
from aiogram.filters import Command
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import select, func
from aiogram.fsm.context import FSMContext
from bot import models, filters, states


async def add_admin_cmd_handler(message: types.Message, state: FSMContext):
    await message.answer(
        text="Пришлите мне ID нового админа:"
    )
    await state.set_state(states.AddAdminStates.get_admin_id)
    # async with session() as open_session:
    #     admin: typing.List[models.sql.Admin] = await open_session.execute(
    #         select([func.count()]).select_from(models.sql.Admin))
    #     admin = admin.scalars().first()


    # await message.answer(f"Всего пользователей: {users_count}")


async def add_admin_handler(message: types.Message, state: FSMContext, session: sessionmaker):
    await state.clear()
    admin_id = message.text
    try:
        await message.bot.send_chat_action(chat_id=admin_id, action="typing")
    except Exception:
        return await message.answer(
            text="Не удалось добавить админа. Убедитесь что вы ввели правильный ID,"
                 " а также у админа есть чат с этим ботом."
        )
    await message.answer(
        text="Новый админ добавлен!\n\n"
             "Удалить админа /deleteadmin"
    )

    async with session() as open_session:
        new_admin = models.sql.Admin(
            id=int(admin_id)
        )
        await open_session.merge(new_admin)
        await open_session.commit()
        # admin: typing.List[models.sql.Admin] = await open_session.execute(
        #     select([func.count()]).select_from(models.sql.Admin))
        # admin = admin.scalars().first()


async def delete_admin_cmd_handler(message: types.Message, state: FSMContext):
    await message.answer(
        text="Пришлите мне ID админа, которого нужно удалить:"
    )
    await state.set_state(states.DeleteAdminStates.get_admin_id)
    # async with session() as open_session:
    #     admin: typing.List[models.sql.Admin] = await open_session.execute(
    #         select([func.count()]).select_from(models.sql.Admin))
    #     admin = admin.scalars().first()


    # await message.answer(f"Всего пользователей: {users_count}")


async def delete_admin_handler(message: types.Message, state: FSMContext, session: sessionmaker):
    await state.clear()
    admin_id = message.text

    if not admin_id.isdecimal():
        return await message.answer(
            text="Не удалось удалить админа. Убедитесь что вы ввели правильный ID."
        )

    admin_id = int(admin_id)

    async with session() as open_session:
        admin: models.sql.Admin = await open_session.execute(
            select(models.sql.Admin).filter_by(id=int(admin_id)))
        admin = admin.scalars().first()

        if not admin:
            await message.answer(
                text="Такого админа нету в базе!"
            )
        else:
            await open_session.delete(admin)
            await open_session.commit()
            await message.answer(text="Админ был удален.")


def setup(dp: Dispatcher):
    dp.message.register(
        add_admin_cmd_handler,
        Command(commands="addadmin"),
        filters.IsBotAdminFilter(True)
    )

    dp.message.register(
        add_admin_handler,
        states.AddAdminStates.get_admin_id,
        filters.IsBotAdminFilter(True)
    )

    dp.message.register(
        delete_admin_cmd_handler,
        Command(commands="deleteadmin"),
        filters.IsBotAdminFilter(True)
    )

    dp.message.register(
        delete_admin_handler,
        states.DeleteAdminStates.get_admin_id,
        filters.IsBotAdminFilter(True)
    )

