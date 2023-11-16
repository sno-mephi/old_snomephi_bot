"""
This module has some internal features for QoL and stuff.
"""
from initializer import *

# admin_module segment
async def db_save():
    await usercoll.save()


async def db_reload():
    await usercoll.reload()


# decorators segment
# logging + checking for authority
def accessor(access_level: int, logging: bool = True):
    def accessor_inner(func: FunctionType):
        async def wrapper(*args):
            msg = args[0]
            if not (isinstance(msg, Message) or isinstance(msg, CallbackQuery) or isinstance(msg, InlineQuery)): 
                return None
            if logging:
                nick = msg.from_user.first_name.replace('<', '&lt;').replace('>', '&gt;')
                await bot.send_message(logchat_id,
                                f'СНО\n'
                                f'Функция <b>{func.__name__}</b>\n\tВызвана пользователем: <a href="tg://user?id={msg.from_user.id}"><b>{nick}</b></a> ({msg.from_user.id})\n\t'
                                f'Данные вызова: <b>{msg.text if isinstance(msg, Message) else (msg.data if isinstance(msg, CallbackQuery) else msg.query)}</b>\n\t'
                                f'Время: {time.ctime(time.time() + 3600 * 3)}', parse_mode='HTML')
            profile = await usercoll.find_one({'id': msg.from_user.id})
            if profile is not None:
                if not access_level or profile['access_level'] >= access_level:
                    try:
                        rslt = await func(*args)
                    except Exception as rslt:
                        await bot.send_message(logchat_id, f'#баг В вызове выше произошла ошибка:\n{str(rslt.args)}')
                    return rslt
            nick = msg.from_user.first_name.replace('<', '&lt;').replace('>', '&gt;')
            await bot.send_message(logchat_id,
                                            f'СНО'
                                            f"ACCESS VIOLATION\n\nПопытка доступа пользователем <a href='tg://user?id={msg.from_user.id}'><b>{nick}</b></a> ({msg.from_user.id})\n\t"
                                            f"Данные вызова: <b>{msg.text if isinstance(msg, Message) else (msg.data if isinstance(msg, CallbackQuery) else msg.query)}</b>\n\t"
                                            f"Время: {time.ctime(time.time() + 3600 * 3)}", parse_mode='HTML')
            if isinstance(msg, Message):
                await msg.reply("Недостаточно прав!")
            elif isinstance(msg, CallbackQuery):
                await bot.answer_callback_query(msg.id, 'Недостаточно прав!', show_alert=True)
            elif isinstance(msg, InlineQuery):
                await bot.answer_inline_query(msg.id, [InlineQueryResultArticle(id='1', title='', description='Не хватает прав!',
                                                input_message_content=InputTextMessageContent(message_text='Не хватает прав!'))])
            return None
        return wrapper
    return accessor_inner


# controlling debugging
@dp.message_handler(commands=['eval'])
@accessor(3)
async def evaluate(message: Message):
    await message.reply(eval(message.text.split('/eval ')[1]))


@dp.message_handler(commands=['asynceval'])
@accessor(3)
async def async_evaluate(message: Message):
    await message.reply(await eval(message.text.split('/asynceval ')[1]))


@dp.message_handler(commands=['rerun'])
@accessor(3)
async def rerun(message: Message):
    await message.reply('Перезагружаем...')
    sys.exit(0)


@dp.message_handler(commands=['save_data'])
@accessor(3)
async def save_data(message: Message):
    await db_save()
    await message.reply('Данные сохранены!')


@dp.message_handler(commands=['reload_data'])
@accessor(3)
async def reload_data(message: Message):
    await db_reload()
    await message.reply('Данные перезагружены!')


@dp.message_handler(regexp=r'^/reg_\d+$')
@accessor(3)
async def reg_admin(message: Message):
    uid = int(message.text.split('_')[1])
    if (await usercoll.find_one({'id': uid, 'access_level': {'$exists': True}})) is not None:
        await message.reply('Такой администратор уже зарегистрирован в системе!')
    elif (await usercoll.find_one({'id': uid})) is not None:
        await usercoll.update_one({'id': uid}, {'$set': {'access_level': 1}})
        await message.reply('Администратор успешно добавлен в систему!')
    else:
        user = {'id': uid, 'access_level': 1}
        await usercoll.insert_one(user)
        await message.reply('Администратор успешно добавлен в систему!')


@dp.message_handler(regexp=r'^/del_\d+$')
@accessor(3)
async def del_user(message: Message):
    uid = int(message.text.split('_')[1])
    if (await usercoll.find_one({'id': uid})) is None:
        await message.reply('Такой администратор в системе не зарегистрирован.')
    elif (await usercoll.find_one({'id': uid, 'access_level': {'$exists': True}})) is None:
        await message.reply('Такой администратор в системе не зарегистрирован.')
    else:
        await usercoll.delete_one({'id': uid})
        await message.reply('Администратор успешно удален из системы!')


# alerts_module section
async def gen_alert_creator_main_message(uid: int) -> Tuple[str, InlineKeyboardMarkup, Union[str, None]]:
    user = await usercoll.find_one({'id': uid})
    keyboard = InlineKeyboardMarkup(row_width=1)
    if user['status'][4] is None:
        keyboard.add(InlineKeyboardButton(text='Добавить фото', callback_data='alert_creator change_photo'))
    else:
        keyboard.add(InlineKeyboardButton(text='Изменить фото', callback_data='alert_creator change_photo'))
        keyboard.add(InlineKeyboardButton(text='Удалить фото', callback_data='alert_creator delete_photo'))
    if user['status'][2] is None:
        keyboard.add(InlineKeyboardButton(text='Добавить текст уведомления', callback_data='alert_creator change_text'))
    else:
        keyboard.add(InlineKeyboardButton(text='Изменить текст уведомления', callback_data='alert_creator change_text'))
    keyboard.add(InlineKeyboardButton(text='Добавить кнопку', callback_data='alert_creator add_button'),
                 *[InlineKeyboardButton(text=str(button['name']), callback_data=f'alert_creator button_preview?id={user["status"][3].index(button)}') for button in user['status'][3]])
    if user['status'][2] is not None:
        keyboard.add(InlineKeyboardButton(text='Предпросмотр', callback_data='alert_creator preview'))
        text = f'<b>Конструктор уведомлений</b>\n\nТекст уведомления:\n{user["status"][2]}\n\nВыберите дальнейшее действие:'
    else:
        text = '<b>Конструктор уведомлений</b>\n\nВыберите дальнейшее действие:'
    keyboard.add(InlineKeyboardButton(text='Отмена', callback_data='reset_status'))
    return text, keyboard, user['status'][4]


async def gen_alert_final(uid: int) -> Tuple[str, InlineKeyboardMarkup, Union[str, None]]:
    user = await usercoll.find_one({'id': uid})
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(*[InlineKeyboardButton(text=button["name"], url=button["url"]) for button in user["status"][3]])
    return user['status'][2], keyboard, user['status'][4], user['status'][5]


async def gen_alert_creator_button_preview(uid: int, bid: int) -> Tuple[str, InlineKeyboardMarkup]:
    user = await usercoll.find_one({'id': uid})
    text = ''
    keyboard = InlineKeyboardMarkup(row_width=1)
    if user['status'][3][bid]['name'] is None:
        keyboard.add(InlineKeyboardButton(text='Добавить текст на кнопку', callback_data=f'alert_creator name_button?id={bid}'))
        text += '<b>Текст на кнопке</b>: <i>не задан</i>\n'
    else:
        keyboard.add(InlineKeyboardButton(text='Изменить текст на кнопке', callback_data=f'alert_creator name_button?id={bid}'))
        text += f'<b>Текст на кнопке</b>: {user["status"][3][bid]["name"]}\n'
    if user['status'][3][bid]['url'] is None:
        keyboard.add(InlineKeyboardButton(text='Добавить ссылку', callback_data=f'alert_creator url_button?id={bid}'))
        text += '<b>Ссылка</b>: <i>не задан</i>\n'
    else:
        keyboard.add(InlineKeyboardButton(text='Изменить ссылку', callback_data=f'alert_creator url_button?id={bid}'))
        text += f'<b>Ссылка</b>: {user["status"][3][bid]["url"]}\n'
    keyboard.add(InlineKeyboardButton(text='Удалить кнопку', callback_data=f'alert_creator delete_button?id={bid}'),
                 InlineKeyboardButton(text='Назад', callback_data='alert_creator main'))
    return text, keyboard


async def gen_salert_creator_button_preview(uid: int, bid: int) -> Tuple[str, InlineKeyboardMarkup]:
    user = await usercoll.find_one({'id': uid})
    text = ''
    keyboard = InlineKeyboardMarkup(row_width=1)
    if user['salert']['buttons'][bid]['title'] is None:
        keyboard.add(InlineKeyboardButton(text='Добавить текст на кнопку', callback_data=f'salert_creators name_button?id={bid}'))
        text += '<b>Текст на кнопке</b>: <i>не задан</i>\n'
    else:
        keyboard.add(InlineKeyboardButton(text='Изменить текст на кнопке', callback_data=f'salert_creators name_button?id={bid}'))
        text += f'<b>Текст на кнопке</b>: {user["salert"]["buttons"][bid]["title"]}\n'
    if user['salert']['buttons'][bid]['link'] is None:
        keyboard.add(InlineKeyboardButton(text='Добавить ссылку', callback_data=f'salert_creators url_button?id={bid}'))
        text += '<b>Ссылка</b>: <i>не задан</i>\n'
    else:
        keyboard.add(InlineKeyboardButton(text='Изменить ссылку', callback_data=f'salert_creators url_button?id={bid}'))
        text += f"<b>Ссылка</b>: {user['salert']['buttons'][bid]['link']}\n"
    keyboard.add(InlineKeyboardButton(text='Удалить кнопку', callback_data=f'salert_creators delete_button?id={bid}'),
                 InlineKeyboardButton(text='Назад', callback_data=PATH_MAIN))
    return text, keyboard


async def update_keyboard(uid: int) -> ReplyKeyboardMarkup:
    user = await usercoll.find_one({'id': uid})
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('Мероприятия недели')
    keyboard.row('Настройка рассылки')
    if 'access_level' in user:
        keyboard.row('Рассылка уведомлений')
    return keyboard
