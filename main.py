"""
This is the main file which just aggregates all other modules into one and initializes connection with TG API.
"""
from initializer import *

from modules.alerts_module import *
from modules.user_module import *


async def startup(dispatcher=dp):
    await bot.send_message(logchat_id, 'Включаемся...')
    # hotfixes
    if not await usercoll.find_one({'id': author_id}):
        await usercoll.insert_one({'id': author_id, 'access_level': 3})


async def shutdown(dispatcher=dp):
    await db_save()
    await bot.send_message(logchat_id, 'Выключаемся...')
    

aiogram.executor.start_polling(dp, skip_updates=True, on_startup=startup, on_shutdown=shutdown, timeout=10)
