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
import sys
import os
import jsondriver
import datetime
import config

tran_tagname = {'maths': 'Математика', 'engineering': 'Инженерия', 'science': 'Естественные науки', 'it': 'IT', 
                'clubs': 'Кружки и клубы', 'conference': 'Конференции', 'olympiad': 'Олимпиады', 'education': 'Образовательные мероприятия',
                'popsci': 'Научно-популярные мероприятия', 'tours': 'Экскурсии'}


TOKEN = config.TOKEN
TOKEN_TEST = config.TOKEN_TEST

bot = aiogram.Bot(TOKEN)
dp = aiogram.Dispatcher(bot)

channel_id = -1001522987203 if True else -1001782239116 # channel to forward requests to # prod / test
post_channel_id = 664519103 if True else -1001782239116 # channel to send posts to # prod / test
author_id = 664519103 # user to autoadd to db as superadmin
logchat_id = 664519103 # chat to send logs to

# setting up data storage
usercoll = jsondriver.AsyncJsonCollection(file_path='db/usercoll.json')
postcoll = jsondriver.AsyncJsonCollection(file_path="db/postcoll.json")

