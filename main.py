"""
This is the main file which just aggregates all other modules into one and initializes connection with TG API.
"""
from initializer import *

from modules.alerts_module import *
from modules.user_module import *


async def startup(dispatcher=dp):
    await bot.send_message(logchat_id, 'Включаемся...')

    # для отправки отложенных сообщений!
    asyncio.create_task(handle_asserts())

    # периодически сохраняем бд на диск
    asyncio.create_task(periodic_handler())

    # hotfixes
    if not await usercoll.find_one({'id': author_id}):
        await usercoll.insert_one({'id': author_id, 'access_level': 3})


async def periodic_handler(period: int = 5):
    while True:
        await db_save()
        await asyncio.sleep(period)


async def shutdown(dispatcher=dp):
    await db_save()
    await bot.send_message(logchat_id, 'Выключаемся...')

aiogram.executor.start_polling(dp, skip_updates=True, on_startup=startup, on_shutdown=shutdown, timeout=10)
