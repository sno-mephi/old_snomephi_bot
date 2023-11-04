"""
This module is used to create event alerts and send it to active users of bot.
"""
from modules.helper_module import *


@dp.message_handler(commands=['new_alert'])
@dp.message_handler(lambda message: message.text == 'Рассылка уведомлений')
@accessor(1)
async def alert_creator_main_text(message: Message):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(text='Добавить фото', callback_data='alert_creator change_photo'),
                 InlineKeyboardButton(text='Добавить текст уведомления', callback_data='alert_creator change_text'),
                 InlineKeyboardButton(text='Добавить кнопку', callback_data='alert_creator add_button'),
                 InlineKeyboardButton(text='Отмена', callback_data='reset_status'))
    msg = await bot.send_message(message.from_user.id, '<b>Конструктор уведомлений</b>\n\nВыберите дальнейшее действие:', reply_markup=keyboard, parse_mode='HTML')
    await usercoll.update_one({'id': message.from_user.id}, {'$set': {'status': ['alert_creator', msg.message_id, None, [], None, []]}})


@dp.callback_query_handler(lambda call: call.data == 'alert_creator main')
@accessor(1)
async def alert_creator_main_call(call: CallbackQuery):
    await usercoll.update_one({'id': call.from_user.id}, {'$set': {'status.0': 'alert_creator'}})
    text, keyboard, photo = await gen_alert_creator_main_message(call.from_user.id)
    if photo is None:
        await call.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    else:
        await call.message.delete()
        msg = await bot.send_photo(call.from_user.id, photo, text, parse_mode='HTML', reply_markup=keyboard)
        await usercoll.update_one({'id': call.from_user.id}, {'$set': {'status.1': msg.message_id}})
    await call.answer()


@dp.callback_query_handler(lambda call: call.data == 'alert_creator change_photo')
@accessor(1)
async def alert_creator_change_photo(call: CallbackQuery):
    await usercoll.update_one({'id': call.from_user.id}, {'$set': {'status.0': 'alert_creator sending_photo'}})
    user = await usercoll.find_one({'id': call.from_user.id})
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='alert_creator main'))
    if user['status'][4] is None:
        await call.message.edit_text('Отправьте фото, прикрепляемое к уведомлению, ответным сообщением.', reply_markup=keyboard)
    else:
        await call.message.delete()
        msg = await bot.send_message(call.from_user.id, 'Отправьте фото, прикрепляемое к уведомлению, ответным сообщением.', reply_markup=keyboard)
        await usercoll.update_one({'id': call.from_user.id}, {'$set': {'status.1': msg.message_id}})
    await call.answer()


@dp.callback_query_handler(lambda call: call.data == 'alert_creator delete_photo')
@accessor(1)
async def alert_creator_delete_photo(call: CallbackQuery):
    await usercoll.update_one({'id': call.from_user.id}, {'$set': {'status.4': None}})
    text, keyboard, _ = await gen_alert_creator_main_message(call.from_user.id)
    await call.message.delete()
    msg = await bot.send_message(call.from_user.id, text, reply_markup=keyboard, parse_mode="HTML")
    await usercoll.update_one({'id': call.from_user.id}, {'$set': {'status.1': msg.message_id}})
    await call.answer()


@dp.callback_query_handler(lambda call: call.data == 'alert_creator change_text')
@accessor(1)
async def alert_creator_text(call: CallbackQuery):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='alert_creator main'))
    user = await usercoll.find_one({'id': call.from_user.id})
    if user['status'][4] is None:
        await call.message.edit_text('Отправьте текст уведомления ответным сообщением.\n\n<b>Основные правила оформления</b>: стандартный HTML-код\n&lt;b&gt;текст&lt;/b&gt; — выделение полужирным\n&lt;i&gt;текст&lt;/i&gt; — выделение курсивом\n&lt;a href=&quot;ссылка&quot;&gt;текст&lt;/a&gt; — гиперссылка',
                                     parse_mode='HTML', reply_markup=keyboard)
        await usercoll.update_one({'id': call.from_user.id}, {'$set': {'status.0': 'alert_creator writing_text'}})
    else:
        await call.message.delete()
        msg = await bot.send_message(call.from_user.id, 'Отправьте текст уведомления ответным сообщением.\n\n<b>Основные правила оформления</b>: стандартный HTML-код\n&lt;b&gt;текст&lt;/b&gt; — выделение полужирным\n&lt;i&gt;текст&lt;/i&gt; — выделение курсивом\n&lt;a href=&quot;ссылка&quot;&gt;текст&lt;/a&gt; — гиперссылка',
                                    parse_mode='HTML', reply_markup=keyboard)
        await usercoll.update_one({'id': call.from_user.id}, {'$set': {'status.0': 'alert_creator writing_text', 'status.1': msg.message_id}})
    await call.answer()


@dp.callback_query_handler(lambda call: call.data == 'alert_creator add_button')
@accessor(1)
async def alert_creator_new_button(call: CallbackQuery):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='alert_creator main'))
    user = await usercoll.find_one({'id': call.from_user.id})
    if user['status'][4] is None:
        await call.message.edit_text('Отправьте текст на кнопке ответным сообщением.', reply_markup=keyboard)
    else:
        await call.message.delete()
        msg = await bot.send_message(call.from_user.id, 'Отправьте текст на кнопке ответным сообщением.', reply_markup=keyboard)
        await usercoll.update_one({'id': call.from_user.id}, {'$set': {'status.1': msg.message_id}})
    user['status'][0] = f'alert_creator naming_button?id={len(user["status"][3])}'
    user['status'][3].append({'name': None, 'url': None})
    await usercoll.update_one({'id': call.from_user.id}, user)
    await call.answer()


@dp.callback_query_handler(lambda call: 'alert_creator button_preview' in call.data)
@accessor(1)
async def alert_creator_preview_button(call: CallbackQuery):
    bid = int(call.data.split('?id=')[1])
    text, keyboard, photo = await gen_alert_creator_button_preview(call.from_user.id, bid)
    if photo is None:
        await call.message.edit_text(text, reply_markup=keyboard, parse_mode='HTML')
    else:
        await call.message.edit_caption(text, reply_markup=keyboard, parse_mode="HTML")
    await call.answer()


@dp.callback_query_handler(lambda call: call.data == 'alert_creator preview')
@accessor(1)
async def alert_creator_preview_full(call: CallbackQuery):
    text, keyboard, photo, _ = await gen_alert_final(call.from_user.id)
    keyboard.add(InlineKeyboardButton(text='Разослать', callback_data='alert_creator alert_stage1'),
                 InlineKeyboardButton(text='Назад', callback_data='alert_creator main'))
    if photo is None:
        await call.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard, disable_web_page_preview=True)
    else:
        await call.message.edit_caption(text, parse_mode='HTML', reply_markup=keyboard)
    await call.answer()


@dp.callback_query_handler(lambda call: call.data == 'alert_creator alert_stage1')
@accessor(1)
async def alert_creator_alert_stage1(call: CallbackQuery):
    user = await usercoll.find_one({'id': call.from_user.id})
    keyboard = InlineKeyboardMarkup(row_width=1)
    if len(user['status'][5]):
        keyboard.add(InlineKeyboardButton(text='Разослать!', callback_data='alert_creator alert_final'))
    keyboard.add(*[InlineKeyboardButton(text=('✅' if tag in user['status'][5] else '') + tran_tagname[tag], callback_data=f'alert_creator toggle?tag={tag}') for tag in tran_tagname],
                 InlineKeyboardButton(text='Назад', callback_data='alert_creator main'))
    if user['status'][4] is None:
        await call.message.edit_text('Выберите тематики, соответствующие данному мероприятию:', reply_markup=keyboard)
    else:
        await call.message.delete()
        msg = await bot.send_message(call.from_user.id, 'Выберите тематики, соответствующие данному мероприятию:', reply_markup=keyboard)
        await usercoll.update_one({'id': call.from_user.id}, {'$set': {'status.1': msg.message_id}})
    await call.answer()


@dp.callback_query_handler(lambda call: 'alert_creator toggle' in call.data)
@accessor(1)
async def alert_creator_toggle(call: CallbackQuery):
    user = await usercoll.find_one({'id': call.from_user.id})
    tag = call.data.split('?tag=')[1]
    if tag in user['status'][5]:
        user['status'][5].remove(tag)
    else:
        user['status'][5].append(tag)
    await usercoll.update_one({'id': call.from_user.id}, user)
    await alert_creator_alert_stage1(call)


@dp.callback_query_handler(lambda call: call.data == 'alert_creator alert_final')
@accessor(1)
async def alert_creator_alert_final(call: CallbackQuery):
    usr = await usercoll.find_one({'id': call.from_user.id})
    text, keyboard, photo, tags = await gen_alert_final(call.from_user.id)
    n = 0
    if photo is None:
        await call.message.edit_text('Начало рассылки. Это может занять некоторое время, подождите...', reply_markup=InlineKeyboardMarkup())
        async for user in usercoll.find({'$or': {tag: True for tag in tags}}):
            try:
                if not len(keyboard.inline_keyboard):
                    kb = await update_keyboard(user['id'])
                    await bot.send_message(user['id'], text, parse_mode='HTML', reply_markup=kb, disable_web_page_preview=True)
                else:
                    await bot.send_message(user['id'], text, parse_mode='HTML', reply_markup=keyboard, disable_web_page_preview=True)
                n += 1
            except aiogram.exceptions.RetryAfter as e:
                await asyncio.sleep(e.timeout + 1)
            except Exception:
                pass
        await bot.send_message(call.from_user.id, f'Уведомления разосланы ({n} успешных отправок)!')
    else:
        await call.message.delete()
        await bot.send_message(call.from_user.id, 'Начало рассылки. Это может занять некоторое время, подождите...')
        async for user in usercoll.find({'$or': {tag: True for tag in tags}}):
            try:
                if not len(keyboard.inline_keyboard):
                    kb = await update_keyboard(user['id'])
                    await bot.send_photo(user['id'], photo, text, parse_mode="HTML", reply_markup=kb)
                else:
                    await bot.send_photo(user['id'], photo, text, parse_mode="HTML", reply_markup=keyboard)
                n += 1
            except aiogram.exceptions.RetryAfter as e:
                await asyncio.sleep(e.timeout + 1)
            except Exception:
                pass
        await bot.send_message(call.from_user.id, f'Уведомления разосланы ({n} успешных отправок)!')
    await call.answer()
    for tag in tags:
        if (await postcoll.find_one({'tag': tag})) is None:
            await postcoll.insert_one({'tag': tag, 'text': text, 'keyboard': usr['status'][3], 'photo': photo})
        else:
            await postcoll.update_one({'tag': tag}, {'$set': {'text': text, 'keyboard': usr['status'][3], 'photo': photo}})
    await usercoll.update_one({'id': call.from_user.id}, {'$unset': {'status': True}})


@dp.callback_query_handler(lambda call: 'alert_creator name_button' in call.data)
@accessor(1)
async def alert_creator_name_button(call: CallbackQuery):
    bid = int(call.data.split('?id=')[1])
    await usercoll.update_one({'id': call.from_user.id}, {'$set': {'status.0': f'alert_creator naming_button?id={bid}'}})
    user = await usercoll.find_one({'id': call.from_user.id})
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='alert_creator main'))
    if user['status'][4] is None:
        await call.message.edit_text('Отправьте текст на кнопке ответным сообщением.', reply_markup=keyboard)
    else:
        await call.message.delete()
        msg = await bot.send_message(call.from_user.id, 'Отправьте текст на кнопке ответным сообщением.', reply_markup=keyboard)
        await usercoll.update_one({'id': call.from_user.id}, {'$set': {'status.1': msg.message_id}})
    await call.answer()


@dp.callback_query_handler(lambda call: 'alert_creator url_button' in call.data)
@accessor(1)
async def alert_creator_url_button(call: CallbackQuery):
    bid = int(call.data.split('?id=')[1])
    await usercoll.update_one({'id': call.from_user.id}, {'$set': {'status.0': f'alert_creator urling_button?id={bid}'}})
    user = await usercoll.find_one({'id': call.from_user.id})
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='alert_creator main'))
    if user['status'][4] is None:
        await call.message.edit_text('Отправьте ссылку, на которую должна вести кнопка, ответным сообщением.', reply_markup=keyboard)
    else:
        await call.message.delete()
        msg = await bot.send_message(call.from_user.id, 'Отправьте ссылку, на которую должна вести кнопка, ответным сообщением.', reply_markup=keyboard)
        await usercoll.update_one({'id': call.from_user.id}, {'$set': {'status.1': msg.message_id}})
    await call.answer()    


@dp.callback_query_handler(lambda call: 'alert_creator delete_button' in call.data)
@accessor(1)
async def alert_creator_delete_button(call: CallbackQuery):
    bid = int(call.data.split('?id=')[1])
    user = await usercoll.find_one({'id': call.from_user.id})
    user['status'][3].pop(bid)
    await usercoll.update_one({'id': call.from_user.id}, user)
    text, keyboard, photo = await gen_alert_creator_main_message(call.from_user.id)
    if photo is None:
        await call.message.edit_text(text, parse_mode='HTML', reply_markup=keyboard)
    else:
        await call.message.delete()
        msg = await bot.send_message(call.from_user.id, text, parse_mode="HTML", reply_markup=keyboard)
        await usercoll.update_one({"id": call.from_user.id}, {"$set": {'status.1': msg.message_id}})
    await call.answer()
