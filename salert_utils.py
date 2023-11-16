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


# проверяет что строка удовлетворяет формату "dd.mm.yyyy hh:mm"
async def is_valid_time(input_str) -> bool:
    try:
        datetime.strptime(input_str, "%d.%m.%Y %H:%M")
        return True
    except ValueError:
        return False


# Обязательно: имя салерта и дата должны быть указаны для его создания, дата должна быть корректной
async def can_finish(salert: dict) -> bool:
    return ((salert['text'] is not None) or (salert['photo'] is not None)) \
        and salert['name'] is not None \
        and await is_correct_time(salert['time'])


# проверяет что время time меньше или равно чем текущее по мск
async def is_correct_time(time_str: str) -> bool:
    given_date = datetime.strptime(time_str, "%d.%m.%Y %H:%M")
    moscow_timezone = pytz.timezone('Europe/Moscow')
    current_date = datetime.now(moscow_timezone)
    given_date = moscow_timezone.localize(given_date)
    return current_date < given_date


# возвращает text, keyboard
# TODO: добавить возвращение фото
async def build_main_message(salert: dict):
    keyboard = InlineKeyboardMarkup(row_width=1)
    photo = None

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
        # TODO: добавить возвращение фото

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
        keyboard.add(InlineKeyboardButton(text='Предпросмотр', callback_data='alert_creator preview'))
        text = f'<b>Конструктор рассылок по таймеру</b>\n\nТекст уведомления:\n{salert["text"]}\n\nВыберите дальнейшее действие:'
    else:
        text = '<b>Конструктор рассылок по таймеру</b>\n\nВыберите дальнейшее действие:'

    keyboard.add(
        InlineKeyboardButton(
            text='Установить таймер',
            callback_data=PATCH_CHANGE_TIME
        ) if salert['time'] is None else InlineKeyboardButton(
            text=f'Изменить таймер ({salert["time"]})',
            callback_data=PATCH_CHANGE_TIME
        )
    )
    keyboard.add(InlineKeyboardButton(text='Отмена', callback_data='reset_status'))

    if await can_finish(salert):
        keyboard.add(InlineKeyboardButton(text='Создать', callback_data='reset_status'))

    return text, keyboard, photo