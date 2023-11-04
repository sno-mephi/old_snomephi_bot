"""
This module is used to parse questions and answers from users and redirect them.
"""
from modules.helper_module import *


# greeting + parsing /start uid_mid from buttons
@dp.message_handler(commands=['start'])
async def start_user(message: Message):
    if (usr := await usercoll.find_one(
            {'id': message.from_user.id, 'name': {'$exists': True}})) is not None and message.text == '/start':
        keyboard = await update_keyboard(message.from_user.id)
        await message.reply('Вы уже зарегистрированы', reply_markup=keyboard)
    elif (
            usr_admin := await usercoll.find_one(
                {'id': message.from_user.id, 'access_level': {'$exists': True}})) is not None:
        if '_' not in message.text:
            uid = int(message.text.split()[1])
            mid = None
        else:
            uid, mid = map(int, message.text.split()[1].split('_'))
        if (user := await usercoll.find_one({'id': uid})) is None:
            await message.reply('Такого пользователя нет в системе!')
            return
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton(text='Отмена', callback_data='reset_status'))
        await bot.send_message(message.from_user.id,
                               f'Вы хотите написать анонимный ответ участнику {user["name"]}?\n\nЕсли это так, отправьте текст сообщения.\nЕсли нет, нажмите кнопку Отмена ниже.',
                               reply_markup=keyboard)
        await usercoll.update_one({'id': message.from_user.id}, {'$set': {'status': ['writing_to', str(uid), None]}})
        if mid is not None:
            new_keyboard = InlineKeyboardMarkup(row_width=1)
            new_keyboard.add(InlineKeyboardButton(text=f'Ответил(-а): {usr["name"]}', callback_data='none'),
                             InlineKeyboardButton(text='Связаться анонимно',
                                                  url=f'https://t.me/snomephi_bot?start={uid}_{mid}'),
                             InlineKeyboardButton(text='Связаться', url=f'tg://user?id={uid}'))
            await bot.edit_message_reply_markup(channel_id, mid, reply_markup=new_keyboard)
    elif usr is None:
        await bot.send_message(message.from_user.id, 'Приветствуем! Введите ФИО для прохождения регистрации.')
        if (await usercoll.find_one({'id': message.from_user.id})) is None:
            await usercoll.insert_one({'id': message.from_user.id})


@dp.message_handler(commands=['help'])
@accessor(0)
async def help(message: Message):
    await bot.send_message(message.from_user.id, 'Это коммуникационный бот Студенческого научного общества НИЯУ МИФИ.'
                                                 '\n\n<b>Функционал</b>:\n'
                                                 '/start — перезагрузка бота\n'
                                                 '/help — вызов этой справки\n'
                                                 'Выбрать мероприятия, напоминания о которых вы хотели бы получать, можно в меню "Настройка рассылки"\n\n'
                                                 'Все текстовые сообщения и файлы видны модераторам.',
                           parse_mode='HTML', reply_markup=await update_keyboard(message.from_user.id))


@dp.message_handler(lambda message: message.text == 'Мероприятия недели')
@accessor(0)
async def history_main(message: Message):
    text = f'<b>Мероприятия этой недели</b>\n\n'
    if (txt_obj := await usercoll.find_one({'id': -2})) is not None:
        text += txt_obj['text']
    else:
        text += '<i>Список мероприятий пока не загружен в систему.</i>'
    await bot.send_message(message.from_user.id, text, parse_mode='HTML',
                           reply_markup=await update_keyboard(message.from_user.id), disable_web_page_preview=True)


@dp.message_handler(lambda message: '/set_history ' in message.text)
@accessor(1)
async def history_set(message: Message):
    text = message.text.replace('/set_history', '').strip()
    if (await usercoll.find_one({'id': -2})) is not None:
        await usercoll.update_one({'id': -2}, {'$set': {'text': text}})
    else:
        await usercoll.insert_one({'id': -2, 'text': text})
    await message.reply('Готово!')


@dp.message_handler(lambda message: message.text == 'Настройка рассылки')
@accessor(0)
async def notifications_settings(message: Message):
    user = await usercoll.find_one({'id': message.from_user.id})
    text = f'<b>Настройка уведомлений</b>\n\nВыберите интересующие вас направления:\n\n' \
           f'<b>Математика</b>\n{"Включено" if user.get("maths", False) else "Выключено"} - /toggle_maths\n\n' \
           f'<b>Инженерия</b>\n{"Включено" if user.get("engineering", False) else "Выключено"} - /toggle_engineering\n\n' \
           f'<b>Естественные науки</b>\n{"Включено" if user.get("science", False) else "Выключено"} - /toggle_science\n\n' \
           f'<b>IT</b>\n{"Включено" if user.get("it", False) else "Выключено"} - /toggle_it\n\n' \
           f'<b>Кружки и клубы</b>\n<i>Занятия студенческих кружков и клубов</i>\n{"Включено" if user.get("clubs", False) else "Выключено"} - /toggle_clubs\n\n' \
           f'<b>Конференции</b>\n<i>Конференции, постерные сессии</i>\n{"Включено" if user.get("conference", False) else "Выключено"} - /toggle_conference\n\n' \
           f'<b>Олимпиады</b>\n<i>Олимпиады и подготовка к ним</i>\n{"Включено" if user.get("olympiad", False) else "Выключено"} - /toggle_olympiad\n\n' \
           f'<b>Образовательные мероприятия</b>\n<i>Школы, интенсивы, мастер-классы</i>\n{"Включено" if user.get("education", False) else "Выключено"} - /toggle_education\n\n' \
           f'<b>Научно-популярные мероприятия</b>\n<i>Science Slam, фестивали, лектории</i>\n{"Включено" if user.get("popsci", False) else "Выключено"} - /toggle_popsci\n\n' \
           f'<b>Экскурсии</b>\n<i>Лаборатории и научно-исследовательские центры</i>\n{"Включено" if user.get("tours", False) else "Выключено"} - /toggle_tours'
    await bot.send_message(message.from_user.id, text, parse_mode='HTML',
                           reply_markup=await update_keyboard(message.from_user.id))



@dp.message_handler(lambda message: '/toggle_' in message.text)
@accessor(0)
async def tags_toggle(message: Message):
    user = await usercoll.find_one({'id': message.from_user.id})
    tag = message.text.split('_')[1]
    if tag in tran_tagname:
        if tag in user:
            await usercoll.update_one({'id': message.from_user.id}, {'$set': {tag: not user[tag]}})
            if not user[tag]:
                await message.reply(f'❌Уведомления о мероприятиях "{tran_tagname[tag]}" выключены.')
            else:
                await message.reply(f'✅Уведомления о мероприятиях "{tran_tagname[tag]}" включены.')
        else:
            await usercoll.update_one({'id': message.from_user.id}, {'$set': {tag: True}})
            await message.reply(f'✅Уведомления о мероприятиях "{tran_tagname[tag]}" включены.')
    else:
        await message.reply('Команда не найдена')


# parsing questions and answers
@dp.message_handler()
@accessor(0)
async def parse_text_message(message: Message):
    user = await usercoll.find_one({'id': message.from_user.id})
    if user is not None and 'status' in user:
        if user['status'][0] == 'writing_to':
            uid = int((await usercoll.find_one({'id': message.from_user.id}))['status'][1])
            keyboard = InlineKeyboardMarkup(row_width=1)
            keyboard.add(InlineKeyboardButton(text='Да, отправить', callback_data='send_anonymously'),
                         InlineKeyboardButton(text='Нет, отредактировать', callback_data='edit_anonymously'),
                         InlineKeyboardButton(text='Отмена', callback_data='reset_status'))
            await bot.send_message(message.from_user.id,
                                   f'Вы хотите написать участнику {(await usercoll.find_one({"id": uid}))["name"]} сообщение:\n{message.text}\n\nВерно?',
                                   parse_mode='HTML', reply_markup=keyboard)
            await usercoll.update_one({'id': message.from_user.id}, {'$set': {'status.2': message.text}})
        # alert_creator segment
        elif user['status'][0] == 'alert_creator writing_text':
            await usercoll.update_one({'id': message.from_user.id},
                                      {'$set': {'status.2': message.text, 'status.0': 'alert_creator'}})
            text, keyboard, photo = await gen_alert_creator_main_message(message.from_user.id)
            if photo is None:
                await bot.edit_message_text(chat_id=message.from_user.id, message_id=user['status'][1], text=text,
                                            parse_mode='HTML', reply_markup=keyboard)
            else:
                await bot.delete_message(message.from_user.id, user['status'][1])
                msg = await bot.send_photo(message.from_user.id, photo, text, parse_mode="HTML", reply_markup=keyboard)
                await usercoll.update_one({'id': message.from_user.id}, {'$set': {'status.1': msg.message_id}})
            await message.delete()
        elif 'alert_creator naming_button' in user['status'][0]:
            bid = int(user['status'][0].split('?id=')[1])
            user['status'][3][bid]['name'] = message.text
            if user['status'][3][bid]['url'] is None:
                keyboard = InlineKeyboardMarkup(row_width=1)
                keyboard.add(InlineKeyboardButton(text='Назад', callback_data='alert_creator main'))
                await bot.edit_message_text(chat_id=message.from_user.id, message_id=user['status'][1],
                                            text=f'<b>Текст на кнопке</b>: {message.text}\n\nОтправьте ссылку, на которую должна вести кнопка, ответным сообщением.',
                                            parse_mode='HTML', reply_markup=keyboard)
                user['status'][0] = f'alert_creator urling_button?id={bid}'
                await usercoll.update_one({'id': message.from_user.id}, user)
            else:
                user['status'][0] = f'alert_creator'
                await usercoll.update_one({'id': message.from_user.id}, user)
                text, keyboard = await gen_alert_creator_button_preview(message.from_user.id, bid)
                await bot.edit_message_text(chat_id=message.from_user.id, message_id=user['status'][1], text=text,
                                            parse_mode='HTML', reply_markup=keyboard)
            await message.delete()
        elif 'alert_creator urling_button' in user['status'][0]:
            bid = int(user['status'][0].split('?id=')[1])
            user['status'][3][bid]['url'] = message.text
            user['status'][0] = f'alert_creator'
            await usercoll.update_one({'id': message.from_user.id}, user)
            text, keyboard = await gen_alert_creator_button_preview(message.from_user.id, bid)
            await bot.edit_message_text(chat_id=message.from_user.id, message_id=user['status'][1], text=text,
                                        parse_mode='HTML', reply_markup=keyboard)
            await message.delete()
    elif user is not None and 'name' not in user:
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton(text='Все верно', callback_data='reg_successful'),
                     InlineKeyboardButton(text='Изменить', callback_data='change_name'))
        await message.reply(f'Проверьте правильность данных: {message.text}', reply_markup=keyboard)
        await usercoll.update_one({'id': message.from_user.id}, {'$set': {'name': message.text}})
    elif user is not None:
        num = (await usercoll.find_one({'id': -1}))['content']
        await usercoll.update_one({'id': -1}, {'$set': {'content': num + 1}})
        msg = await bot.send_message(channel_id,
                                     f'#вопрос №{num + 1}\n<b>Пользователь:</b> {user["name"]}\n<b>Текст обращения:</b> {message.text}\n\n<b>Время обращения: </b>{time.ctime(time.time() + 3600 * 3)}',
                                     parse_mode='HTML')
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            InlineKeyboardButton(text='Ответил(-а)', callback_data=f'question_answered?uid={message.from_user.id}'),
            InlineKeyboardButton(text='Связаться анонимно',
                                 url=f'https://t.me/snomephi_bot?start={message.from_user.id}_{msg.message_id}'),
            InlineKeyboardButton(text='Связаться', url=f'tg://user?id={message.from_user.id}'))
        await msg.edit_reply_markup(keyboard)
        await message.reply('Ваш вопрос отправлен, ожидайте ответа.')


@dp.message_handler(content_types=ContentType.DOCUMENT)
async def parse_doc_message(message: Message):
    user = await usercoll.find_one({'id': message.from_user.id})
    if message.from_user.id == 664519103:
        await bot.send_message(664519103, f'FILE_ID: {message.document.file_id}')
    if user is not None and 'status' in user:
        uid = int((await usercoll.find_one({'id': message.from_user.id}))['status'][1])
        await message.document.download(destination_file=f'db/{message.document.file_name}')
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton(text='Да, отправить', callback_data='send_anonymously'),
                     InlineKeyboardButton(text='Отмена', callback_data='reset_status'))
        await bot.send_document(message.from_user.id, document=InputFile(f'db/{message.document.file_name}',
                                                                         filename=message.document.file_name),
                                caption=f'Вы хотите написать участнику {(await usercoll.find_one({"id": uid}))["name"]} сообщение:\n{message.caption}\n\nВерно?',
                                reply_markup=keyboard, parse_mode='HTML')
        await usercoll.update_one({'id': message.from_user.id}, {
            '$set': {'status.2': {'file_name': message.document.file_name, 'caption': message.caption}}})
    elif user is not None:
        await message.document.download(destination_file=f'db/{message.document.file_name}')
        num = (await usercoll.find_one({'id': -1}))['content']
        await usercoll.update_one({'id': -1}, {'$set': {'content': num + 1}})
        if not message.caption:
            msg = await bot.send_document(channel_id, document=InputFile(f'db/{message.document.file_name}',
                                                                         filename=message.document.file_name),
                                          caption=f'#вопрос №{num + 1}\n<b>Пользователь:</b> {user["name"]}\n<b>Время обращения: </b>{time.ctime(time.time() + 3600 * 3)}',
                                          parse_mode='HTML')
        else:
            msg = await bot.send_document(channel_id, document=InputFile(f'db/{message.document.file_name}',
                                                                         filename=message.document.file_name),
                                          caption=f'#вопрос №{num + 1}\n<b>Пользователь:</b> {user["name"]}\n<b>Текст обращения:</b> {message.caption}\n\n<b>Время обращения: </b>{time.ctime(time.time() + 3600 * 3)}',
                                          parse_mode='HTML')
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton(text='Связаться анонимно',
                                          url=f'https://t.me/snomephi_bot?start={message.from_user.id}_{msg.message_id}'),
                     InlineKeyboardButton(text='Связаться', url=f'tg://user?id={message.from_user.id}'))
        await msg.edit_reply_markup(keyboard)
        await message.reply('Ваш вопрос отправлен и получен. Ожидайте ответа!')


@dp.message_handler(content_types=ContentType.PHOTO)
async def parse_photo_message(message: Message):
    user = await usercoll.find_one({'id': message.from_user.id})
    if user is not None and 'status' in user and user['status'][0] == 'alert_creator sending_photo':
        await usercoll.update_one({'id': message.from_user.id}, {"$set": {'status.4': message.photo[0].file_id}})
        text, keyboard, photo = await gen_alert_creator_main_message(message.from_user.id)
        await bot.delete_message(message.from_user.id, user['status'][1])
        msg = await bot.send_photo(message.from_user.id, photo, text, parse_mode="HTML", reply_markup=keyboard)
        await usercoll.update_one({'id': message.from_user.id},
                                  {'$set': {'status.0': 'alert_creator', 'status.1': msg.message_id}})
        await message.delete()
    else:
        await parse_incompatible_message(message)


@dp.message_handler(content_types=ContentType.ANY)
async def parse_incompatible_message(message: Message):
    await message.reply(
        'Забыли предупредить: бот поддерживает отправку только текстовых сообщений или вложений в виде файлов. ')


# registration things
@dp.callback_query_handler(lambda call: call.data == 'reg_successful')
@accessor(0)
async def reg_user_final(call: CallbackQuery):
    await call.message.delete_reply_markup()
    keyboard = await update_keyboard(call.from_user.id)
    await call.message.delete()
    await bot.send_message(call.from_user.id,
                           'Регистрация прошла успешно. Задайте интересующий вопрос ответным сообщением.',
                           reply_markup=keyboard)
    await call.answer()
    await usercoll.update_one({'id': call.from_user.id}, {
        '$set': {'maths': True, 'engineering': True, 'science': True, 'it': True, 'conference': True, 'olympiad': True,
                 'education': True, 'popsci': True, 'tours': True}})
    await help(call)


@dp.callback_query_handler(lambda call: call.data == 'change_name')
@accessor(0)
async def reg_user_edit(call: CallbackQuery):
    await call.message.delete_reply_markup()
    await call.message.edit_text('Введите свое ФИО.')
    await usercoll.update_one({'id': call.from_user.id}, {'$unset': {'name': True}})
    await call.answer()


# answering things
@dp.callback_query_handler(lambda call: 'question_answered' in call.data)
@accessor(1)
async def question_answered(call: CallbackQuery):
    uid = int(call.data.split('?uid=')[1])
    user = await usercoll.find_one({'id': call.from_user.id})
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(text=f'Ответил(-а): {user["name"]}', callback_data='none'),
                 InlineKeyboardButton(text='Связаться анонимно',
                                      url=f'https://t.me/snomephi_bot?start={uid}_{call.message.message_id}'),
                 InlineKeyboardButton(text='Связаться', url=f'tg://user?id={uid}'))
    await call.message.edit_reply_markup(keyboard)
    await call.answer()


@dp.callback_query_handler(lambda call: call.data == 'reset_status')
@accessor(1)
async def reset_status(call: CallbackQuery):
    await call.message.delete()
    await usercoll.update_one({'id': call.from_user.id}, {'$unset': {'status': True}})
    await call.answer()


@dp.callback_query_handler(lambda call: call.data == 'send_anonymously')
@accessor(1)
async def send_anonymously(call: CallbackQuery):
    status = (await usercoll.find_one({'id': call.from_user.id}))['status']
    if isinstance(status[2], dict):
        await bot.send_document(int(status[1]),
                                document=InputFile(f'db/{status[2]["file_name"]}', filename=status[2]["file_name"]),
                                caption=f'Сообщение от руководства СНО:\n\n{status[2]["caption"]}\n\nТеперь вы можете написать ответное сообщение.',
                                parse_mode='HTML')
        await call.message.delete()
        await bot.send_message(call.from_user.id, 'Сообщение отправлено!')
    else:
        await bot.send_message(int(status[1]), 'Ответ на вопрос:\n\n' + status[
            2] + '\n\nОстались вопросы? Задайте их в ответном сообщении.', parse_mode='HTML')
        await call.message.delete_reply_markup()
        await call.message.edit_text('Сообщение отправлено!')
    await usercoll.update_one({'id': call.from_user.id}, {'$unset': {'status': True}})
    await call.answer()


@dp.callback_query_handler(lambda call: call.data == 'edit_anonymously')
@accessor(1)
async def edit_anonymously(call: CallbackQuery):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(text='Отмена', callback_data='reset_status'))
    await call.message.edit_reply_markup(keyboard)
    await call.message.edit_text('Отправьте новый текст сообщения.')
    await usercoll.update_one({'id': call.from_user.id}, {'$set': {'status.2': None}})
    await call.answer()


# QoL for call loading not to appear forever
@dp.callback_query_handler()
@accessor(1)
async def weird_call(call: CallbackQuery):
    await call.answer()
