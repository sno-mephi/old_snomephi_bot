"""
This part is where all the internal variables and storages are being unitedly initialized for usage in other modules.
"""
from types import FunctionType
from typing import List, Union, Tuple, Dict
import time
import aiogram
from aiogram.types import *
import asyncio
import aiohttp
import pytz
import re
from datetime import datetime
import sys
import os
import jsondriver
import datetime
from salert_utils import *
import config

tran_tagname = {'maths': 'Математика', 'engineering': 'Инженерия', 'science': 'Естественные науки', 'it': 'IT', 
                'clubs': 'Кружки и клубы', 'conference': 'Конференции', 'olympiad': 'Олимпиады', 'education': 'Образовательные мероприятия',
                'popsci': 'Научно-популярные мероприятия', 'tours': 'Экскурсии', 'scientific_seminars': 'Научные семинары'}


TOKEN = config.TOKEN

bot = aiogram.Bot(TOKEN)
dp = aiogram.Dispatcher(bot)

channel_id = -1001522987203 # id админского чата
author_id = 664519103  # id автора
logchat_id = 664519103 # id чата куда пишутся логи
db_path = "db_prod"

# если есть флаг testing, то: @idfed09 админ, логи и прочее пишем в эту беседу
# (пишите мне в лс для добавления)
if "--testing" in sys.argv:
    channel_id = -1002057270905
    author_id = 920061911
    logchat_id = -1002057270905
    db_path = "db_test"


# setting up data storage
usercoll = jsondriver.AsyncJsonCollection(file_path=db_path+'/usercoll.json')
postcoll = jsondriver.AsyncJsonCollection(file_path=db_path+"/postcoll.json")
salerts = jsondriver.AsyncJsonCollection(file_path=db_path+'/salerts.json')    # бд рассылок по таймеру

