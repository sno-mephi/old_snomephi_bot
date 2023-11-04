from aiohttp import web
from aiogram import Bot, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.webhook import SendMessage, get_new_configured_app
import aiogram.utils.markdown as fmt
import urllib

import asyncio

from random import randint
from os import getenv
from sys import exit
from aiogram import types

import enum

class workStatus(enum.Enum):
    clean = 0
    latex = 1
    wiki = 2

workFlag = workStatus.clean

import os, requests
import aiohttp

async def getPngLatex( formula, file, negate=False ):
    tfile = file
    if negate:
        tfile = 'tmp.png'
    r = requests.get('http://latex.codecogs.com/png.latex?\dpi{300} \huge %s' % formula)
    f = open( tfile, 'wb' )
    f.write( r.content )
    f.close()
    if negate:
        os.system( 'convert tmp.png -channel RGB -negate -colorspace rgb %s' %file )

def getSvgLatex(formula, file):
    url = "https://math.vercel.app?from=%s" % formula
    req = requests.get(url)
    f = open(file, 'wb')
    f.write(req.content)
    f.close()

async def getPNG(msg: str):
    raw_str = r'{}'.format(msg)
    try:
        await getPngLatex(raw_str, 'reg_levin.png', True )
    except aiohttp.client_exceptions.ClientOSError as ex:
        pass

async def getSVG(msg: str):
    raw_str = r'{}'.format(msg)
    try:
        getSvgLatex(raw_str, 'tmp.svg')
    except Exception as ex:
        print(ex)

import wikipedia

async def getWikiPage(msg: str):
    try:
        pageUrl = wikipedia.page(msg).url
    except wikipedia.DisambiguationError as e:
        s = e.options[0]
        pageUrl = wikipedia.page(s).url
    except wikipedia.exceptions.PageError:
        pageUrl = 'Не найдено...'
    return pageUrl

# Объект бота
bot = Bot(token="6272715291:AAHfBPOaMvYZGCyGC92qLOq9iuObR96lPo8", parse_mode=types.ParseMode.HTML)
# Диспетчер для бота
dp = Dispatcher(bot)

usersStatus = dict()

# Режимы работы программы
# 0 -- дефолтный
# 1 -- латех
# 2 -- список литературы

@dp.message_handler(commands="info")
async def cmd_info(message: types.Message):
    global usersStatus
    usersStatus[message.from_id] = workStatus.clean

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons1 = ["Перевод формулы из LaTeX в PNG", "Поиск статей в англоязычной википедии"]
    buttons2 = ["Шаблоны", "Очистить выбор"]
    buttons3 = ["Информация", "FAQ"]
    keyboard.add(*buttons1)
    keyboard.add(*buttons2)
    keyboard.add(*buttons3)
    await message.answer(
        fmt.text(
            fmt.text("Информация обо мне."),
            fmt.text("У меня есть различные режимы работы программы:"),
            fmt.text("LaTeX -- напиши /LaTeX, после чего отправь код формулы на языке разметки LaTeX. Бот отправит картинку с формулой."),
            fmt.text("Поиск по википедии -- напиши /wiki, потом название статьи, которую хочешь найти. Бот выведет ссылку на запрос."),
            fmt.text("Шаблоны -- напиши /template, после выбери подходящий шаблон."),
            fmt.text("Также есть некоторые команды:"),
            fmt.text("Очистить выбор -- напиши /clean, чтобы бот не реагировал на сообщения."),
            fmt.text("Узнать информацию обо мне -- напиши /info."),
            fmt.text("Узнать наши контакты -- напиши /faq"),
            fmt.text("Кинуть кубик -- /dice."),
            sep="\n"
                ), parse_mode="HTML", reply_markup=keyboard
    )

@dp.message_handler(commands="start")
async def cmd_hello(message: types.Message):
    global usersStatus
    usersStatus[message.from_id] = workStatus.clean
    await message.reply(
        fmt.text(
            fmt.text("Привет, я бот из Школы", fmt.hunderline("Актива"), "НИЯУ МИФИ!"),
            sep="\n"
                ), parse_mode="HTML"
    )
    await cmd_info(message)

#-----------------------------------------------------------------------#

@dp.message_handler(lambda message: message.text == "/LaTeX" or message.text == "Перевод формулы из LaTeX в PNG")
async def LaTeX_button(message: types.Message):
    global usersStatus
    usersStatus[message.from_id] = workStatus.latex
    await message.reply("Напишите формулу в формате LaTeX.")

@dp.message_handler(lambda message: message.text == "/wiki" or message.text == "Поиск статей в англоязычной википедии")
async def wiki_button(message: types.Message):
    global usersStatus
    usersStatus[message.from_id] = workStatus.wiki
    await message.reply("Введите название статьи, которую вы хотите найти в Википедии.")

@dp.message_handler(lambda message: message.text == "/clean" or message.text == "Очистить выбор")
async def clear_button(message: types.Message):
    global usersStatus
    usersStatus[message.from_id] = workStatus.clean
    await message.reply("Выбор очищен.")

@dp.message_handler(lambda message: message.text == "Информация")
async def clear_button(message: types.Message):
    global usersStatus
    usersStatus[message.from_id] = workStatus.clean
    await cmd_info(message)

#-----------------------------------------------------------------------#
@dp.message_handler(lambda message: message.text == "FAQ" or message.text == "/faq")
async def cmd_fuck(message: types.Message):
    global usersStatus
    usersStatus[message.from_id] = workStatus.clean
    await message.answer(
        fmt.text(
            fmt.text("Если у Вас остались вопросы или предложения:"),
            fmt.text("Telegramm: @snomephi"),
            fmt.text("Email: sno@mephi.ru"),
            fmt.text("Web: sno.mephi.ru"),
            sep="\n"
        ))
    
@dp.message_handler(lambda message: message.text == "Шаблоны" or message.text == "/templates")
async def cmd_inline_url(message: types.Message):
    global usersStatus
    usersStatus[message.from_id] = workStatus.clean
    buttons = [
        types.InlineKeyboardButton(text="ВКР", callback_data = "VKR"),
        types.InlineKeyboardButton(text="Дневники практик", callback_data = "Dnev"),
        types.InlineKeyboardButton(text="Презентации", callback_data = "Prez"),
        types.InlineKeyboardButton(text="Логотипы МИФИ и институтов", callback_data = "Logo"),
        types.InlineKeyboardButton(text="Оформление списка литературы", callback_data = "Liter")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    await message.answer("Выберите тип работы:", reply_markup=keyboard)

@dp.callback_query_handler(text="Dnev")
async def cmd_dnev(call: types.CallbackQuery):
    buttons = [
        types.InlineKeyboardButton(text="Магистр", callback_data = "Mag"),
        types.InlineKeyboardButton(text="Бакалавр", callback_data = "Bag"),
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    await call.message.answer("Выберите:", reply_markup=keyboard)

@dp.callback_query_handler(text="Mag")
async def cmd_mag(call: types.CallbackQuery):
    await call.message.answer("Дневники практик для магистров")
    msgs = await call.message.answer_media_group(mag)
    for msg in msgs:
        pass
        #await bot.send_message(664519103, f'FILE_ID: {msg.document.file_id}')

@dp.callback_query_handler(text="Bag")
async def cmd_bac(call: types.CallbackQuery):
    await call.message.answer("Дневники практик для бакалавров")
    msgs = await call.message.answer_media_group(bag)
    for msg in msgs:
        pass
        #await bot.send_message(664519103, f'FILE_ID: {msg.document.file_id}')

@dp.callback_query_handler(text="VKR")
async def cmd_vkr(call: types.CallbackQuery):
    await call.message.answer("Шаблоны ВКР")
    msgs = await call.message.answer_media_group(vkr)
    for msg in msgs:
        pass
        #await bot.send_message(664519103, f'FILE_ID: {msg.document.file_id}')

@dp.callback_query_handler(text="Prez")
async def cmd_prez(call: types.CallbackQuery):
    await call.message.answer("Примеры презентаций")
    msg = await call.message.answer_media_group(prez)
    #await bot.send_message(664519103, f'FILE_ID: {msg[0].document.file_id}')

@dp.callback_query_handler(text="Logo")
async def cmd_logo(call: types.CallbackQuery):
    await call.message.answer("Логотипы МИФИ и институтов")
    msgs = await call.message.answer_media_group(logo)
    for msg in msgs:
        pass
        #await bot.send_message(664519103, f'FILE_ID: {msg.document.file_id}')

@dp.callback_query_handler(text="Liter")
async def cmd_litres(call: types.CallbackQuery):
    await call.message.answer("Оформление списка литературы")
    msg = await call.message.answer_media_group(liter)
    #await bot.send_message(664519103, f'FILE_ID: {msg[0].document.file_id}')

@dp.message_handler(commands="dice")
async def cmd_dice(message: types.Message):
    await message.answer_dice(emoji="🎲")

#-----------------------------------------------------------------------#

vkr = types.MediaGroup()
vkr.attach_document("BQACAgIAAxkDAAIF_mRaswstVvUnAVEFUOyFAoEjZs4LAALUMAACU5bZSlYwIiGUV5pELwQ", "")
vkr.attach_document("BQACAgIAAxkDAAIF_2RaswsHNl5iianGF8whI6gozPp5AALVMAACU5bZSob0ic1yIhvyLwQ", "")


mag = types.MediaGroup()
mag.attach_document("BQACAgIAAxkDAAIGCWRasxa9iLuVZEZ7CjllO27X8PEHAALXMAACU5bZSmtNBWmfsoDRLwQ", "")
mag.attach_document("BQACAgIAAxkDAAIGCmRasxY2EY0Xf4D9Px-x6b3gOoojAALYMAACU5bZSsTVdEYOJmeKLwQ", "")
mag.attach_document("BQACAgIAAxkDAAIGC2RasxbdGorLkro0BZ781Bry6OWEAALWMAACU5bZSlEIGlXlG_0DLwQ", "")

bag = types.MediaGroup()
bag.attach_document("BQACAgIAAxkDAAIGEGRasxn7Dd0I7aS_MTNDbn3g136KAALaMAACU5bZSktZkoubYdZ6LwQ", "")
bag.attach_document("BQACAgIAAxkDAAIGEWRasxlJxdea2EfvHuyNhDUN0c2SAALZMAACU5bZSmFNr9Yldu8mLwQ", "")


prez = types.MediaGroup()
prez.attach_document("BQACAgIAAxkDAAIGGWRasyCJ3t-8K0Ey2rmNAbJ4FFL1AALbMAACU5bZSme5fDnvVdjfLwQ", "")

logo = types.MediaGroup()
logo.attach_document("BQACAgIAAxkDAAIGHGRasyRru5xN4qVN5_gvyhjA5mCqAALcMAACU5bZSmkkdU3u7K2RLwQ", "")
logo.attach_document("BQACAgIAAxkDAAIGHWRasySLQ62b9nvrbx4qp2Qv5X7YAALdMAACU5bZSsmCJi36Di2BLwQ", "")

liter = types.MediaGroup()
liter.attach_document("BQACAgIAAxkDAAIGYmRatFfpGoqb2kqEno2PS18YQYZwAALhMAACU5bZSp0dRRkR07ZyLwQ", "")

#-----------------------------------------------------------------------#

@dp.message_handler()
async def any_text_message2(message: types.Message):
    global usersStatus
    if (usersStatus[message.from_id] == workStatus.clean):
      pass
    elif (usersStatus[message.from_id] == workStatus.latex):
        await getPNG(message.text)
        await getSVG(message.text)
        await message.answer_document(types.InputFile('tmp.png', 'Формула.png'), caption="Изображение по вашему запросу.")
        await message.answer_document(types.InputFile('tmp.svg', 'Формула.svg'))
    elif (usersStatus[message.from_id] == workStatus.wiki):
        url = await getWikiPage(message.text)
        await message.answer(url)
    else:
        await message.answer("Undefined behaivor")

#-----------------------------------------------------------------------#
executor.start_polling(dp, skip_updates=True)
