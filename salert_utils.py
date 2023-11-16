from datetime import datetime

import pytz
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

PATCH_CHANGE_PHOTO = 'salert_creator change_photo'
PATCH_DELETE_PHOTO = 'salert_creator delete_photo'
PATCH_CHANGE_TEXT = 'salert_creator change_text'
PATCH_ADD_BUTTON = 'salert_creator add_button'
PATCH_CHANGE_TIME = 'salert_creator change_time'
PATH_MAIN = 'salert-creator main'

STATUS_CREATOR = 'salert_creator'
STATUS_SENDING_PHOTO = 'salert_creator sending photo'
STATUS_WRITING_TEXT = 'salert_creator writing text'
STATUS_NAMING_BUTTON = 'salert naming but'
STATUS_LINKING_BUTTON = 'salert linking but'
STATUS_SENDING_TIME = 'salert sending time'
SET_SALERT_NAME = 'salerts set job name'
WRITING_SALERT_NAME = 'job waiting salert name'
SALERT_CREATE_PLAN = 'salert planning add'
SALERTS_JOBS_LIST_CALLBACK = 'salerts list callback'


# проверяет что строка удовлетворяет формату "dd.mm.yyyy hh:mm"
async def is_valid_time(input_str) -> bool:
    try:
        datetime.strptime(input_str, "%d.%m.%Y %H:%M")
        return True
    except ValueError:
        return False
    except Exception:
        return False


# Обязательно: имя салерта и дата должны быть указаны для его создания, дата должна быть корректной
async def can_finish(salert: dict) -> bool:
    return ((salert['text'] is not None) or (salert['photo'] is not None)) \
        and salert['time'] is not None \
        and await is_correct_time(salert['time'])


# проверяет что время time меньше или равно чем текущее по мск
async def is_correct_time(time_str: str) -> bool:
    if time_str is None:
        return False
    try:
        given_date = datetime.strptime(time_str, "%d.%m.%Y %H:%M")
        moscow_timezone = pytz.timezone('Europe/Moscow')
        current_date = datetime.now(moscow_timezone)
        given_date = moscow_timezone.localize(given_date)
    except Exception:
        return False
    return current_date < given_date


# для построения сообщений салертов
async def build_salert_message(salert: dict):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(*[InlineKeyboardButton(text=button["title"], url=button["link"]) for button in salert['buttons']])
    return salert['text'], salert['photo'], keyboard

async def build_main_message(salert: dict):
    keyboard = InlineKeyboardMarkup(row_width=1)

    keyboard.add(
        InlineKeyboardButton(
            text='Добавить фото',
            callback_data=PATCH_CHANGE_PHOTO
        ) if salert['photo'] is None else InlineKeyboardButton(
            text='Изменить фото',
            callback_data=PATCH_CHANGE_PHOTO
        )
    )

    if salert['photo'] is not None:
        keyboard.add(
            InlineKeyboardButton(
                text='Удалить фото',
                callback_data=PATCH_DELETE_PHOTO
            )
        )

    keyboard.add(
        InlineKeyboardButton(
            text='Добавить текст рассылки',
            callback_data=PATCH_CHANGE_TEXT
        ) if salert['text'] is None else InlineKeyboardButton(
            text='Изменить текст рассылки',
            callback_data=PATCH_CHANGE_TEXT
        )
    )

    keyboard.add(
        InlineKeyboardButton(
            text='Добавить кнопку',
            callback_data=PATCH_ADD_BUTTON
        )
    )

    if salert['buttons'] is not None:
        keyboard.add(*[InlineKeyboardButton(text=button["title"], callback_data=f'salert_creators button_preview?id={salert["buttons"].index(button)}') for button in salert['buttons']])
        #keyboard.add(*[InlineKeyboardButton(text=button["title"], url=button["link"]) for button in salert['buttons']])

    if salert['text'] is not None:
        keyboard.add(InlineKeyboardButton(text='Предпросмотр', callback_data='salert_creators preview'))
        text = f'<b>Конструктор рассылок по таймеру</b>\n\nТекст уведомления:\n{salert["text"]}'
    else:
        text = '<b>Конструктор рассылок по таймеру</b>'

    keyboard.add(
        InlineKeyboardButton(
            text='Установить таймер',
            callback_data=PATCH_CHANGE_TIME
        ) if salert['time'] is None else InlineKeyboardButton(
            text=f'Изменить таймер ({salert["time"]})',
            callback_data=PATCH_CHANGE_TIME
        )
    )

    # TODO: добавить редактирование!
    if await can_finish(salert):
        if salert['name'] is None:
            keyboard.add(InlineKeyboardButton(text='Установить имя задачи', callback_data=SET_SALERT_NAME))
        else:
            keyboard.add(InlineKeyboardButton(text='Поставить в очередь! (нелья редачить)', callback_data=SALERT_CREATE_PLAN))
            text += f"\n\nИмя отложенной задачи: {salert['name']}"

    keyboard.add(InlineKeyboardButton(text='Отмена', callback_data='reset_status'))

    text += "\n\nВыберите дальнейшее действие:"
    return text, keyboard, salert['photo']
