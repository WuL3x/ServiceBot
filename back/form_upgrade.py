# import sqlite3
# import time
# import uuid
#
# from aiogram import types
# from aiogram.dispatcher import FSMContext
# from aiogram.dispatcher.filters import Text
# from aiogram.dispatcher.filters.state import State, StatesGroup
# from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
#
# from back.keyboards import kb1
# from config import CHANNEL_ID
# from keyboards import bt_sec
# from main import bot, dp, generate_order_id
#
# button_cancel = types.InlineKeyboardButton('Отмена', callback_data='cancel')
# cancelButton = types.ReplyKeyboardMarkup(resize_keyboard=True).add(button_cancel)
# USER_DATA_UP = {}
#
#
# # НЕ ДОДЕЛАН НУ И В ПИЗДУ
# @dp.callback_query_handler(text=['Меню'])
# async def main_menu(callback: types.callback_query):
#     await bot.send_message(callback.from_user.id, reply_markup=kb1, text='Выберите пункт меню 👇🏻')
#
#
# def upgrade():
#     class UpgradeForm(StatesGroup):
#         issue = State()
#         name = State()
#         phone = State()
#         confirm = State()
#
#     @dp.callback_query_handler(text='upgrade')
#     async def register_order(callback: types.callback_query, state: FSMContext):
#         await bot.send_message(callback.from_user.id,
#                                f'''{callback.from_user.username}, мы просим Вас указывать полную информацию об
# устройстве и описывать ТЗ максимально развернуто.''',
#                                reply_markup=cancelButton)
#         async with state.proxy() as data:
#             data['id_client'] = callback.from_user.id
#             data['user_name'] = callback.from_user.username
#             data['id_order'] = generate_order_id()
#             data['device'] = 'ПК'
#             data['dev_name'] = 'ПК'
#         await bot.send_message(callback.from_user.id, 'Опишите, что Вы хотите модернизировать.',
#                                reply_markup=cancelButton)
#         await UpgradeForm.issue.set()
#
#     @dp.message_handler(state='*', commands='cancel')
#     @dp.message_handler(Text(equals='Отмена', ignore_case=True), state='*')
#     async def cancel(message: types.message, state: FSMContext):
#         current_state = await state.get_state()
#         if current_state is None:
#             return
#
#         await bot.send_message(message.from_user.id, text='''Отмена отправки⛔''', reply_markup=bt_sec)
#         time.sleep(1)
#         await main_menu(message)
#         await state.finish()
#
#     @dp.message_handler(state=UpgradeForm.issue)
#     async def process_issue(message: types.Message, state: FSMContext):
#         async with state.proxy() as data:
#             data['issue'] = message.text
#
#         await message.reply("Введите Ваши фаимилию и имя.", reply=False, reply_markup=cancelButton)
#         await UpgradeForm.name.set()
#
#     @dp.message_handler(state=UpgradeForm.name)
#     async def process_name(message: types.Message, state: FSMContext):
#         async with state.proxy() as data:
#             data['name'] = message.text
#
#         phone_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
#         share = KeyboardButton(text="Отправить контакт", request_contact=True)
#         phone_keyboard.add(share).row(button_cancel)
#         await message.answer("Пожалуйста, отправьте свой контактный номер телефона или введите его вручную",
#                              reply_markup=phone_keyboard)
#         await UpgradeForm.phone.set()
#
#     @dp.message_handler(state=UpgradeForm.phone, content_types=[types.ContentType.TEXT, types.ContentType.CONTACT])
#     async def process_phone(message: types.Message, state: FSMContext):
#         if message.contact:
#             phone = message.contact.phone_number
#         else:
#             phone = message.text
#
#         async with state.proxy() as data:
#             data['phone'] = phone
#             await state.update_data(data)
#
#             # формируем сообщение
#             text = f"Заявка\n"
#             text += f"Модернизация устройства\n"
#             text += f"Номер заявки: {data['id_order']}\n"
#             text += f"Что модернизировать : {data['issue']}\n"
#             text += f"Имя: {data['name']}\n"
#             text += f"Телефон: {data['phone']}\n"
#
#             kb_con = types.InlineKeyboardMarkup()
#             kb_con.insert(types.InlineKeyboardButton(text="Все верно", callback_data='confirm:verno'))
#             kb_con.add(types.InlineKeyboardButton(text="Нет. Есть ошибка", callback_data='confirm:error'))
#
#             # отправляем сообщение пользователю
#             await bot.send_message(chat_id=message.from_user.id, text=text, parse_mode=ParseMode.HTML,
#                                    reply_markup=kb_con)
#         await UpgradeForm.confirm.set()
#
#     @dp.callback_query_handler(state=UpgradeForm.confirm)
#     async def process_confirm(callback: types.CallbackQuery, state: FSMContext):
#         # обрабатываем ответ на кнопку
#         if callback.data.split(':')[1] == 'error':
#             reank = types.InlineKeyboardMarkup()
#             reank.insert(types.InlineKeyboardButton(text="Оставить заявку", callback_data="upgrade"))
#             await bot.send_message(callback.from_user.id, "Пройдите опрос снова.",
#                                    reply_markup=reank)
#             async with state.proxy() as data:
#                 data['user_name'] = callback.from_user.first_name
#                 data['id_order'] = data['id_order']
#
#
#
#         elif callback.data.split(':')[1] == 'verno':
#             async with state.proxy() as data:
#                 text = f"Модернизация:\n"
#                 text += f"TG user name: @{data['user_name']}\n"
#                 text += f"TG_ID: {callback.from_user.id}\n"
#                 text += f"Номер заявки: {data['id_order']}\n"
#                 text += f"Что модернизировать : {data['issue']}\n"
#                 text += f"Имя: {data['name']}\n"
#                 text += f"Телефон: {data['phone']}\n"
#             USER_DATA_UP=[data['device'], data['user_name'], data['id_order'], data['dev_name'], data['issue'],
#                          data['name'], data['phone'], data['id_client']]
#             kb_chat = InlineKeyboardMarkup()
#             kb_chat.add(InlineKeyboardButton(text="Перейти в чат",
#                                              url=f"t.me/{callback.from_user.username}"))
#             kb_chat.add(
#                 InlineKeyboardButton(text='Подтвердить заявку',
#                                      callback_data=f"confirm_upgrade:{data['id_order']}:yes"))
#             kb_chat.add(
#                 InlineKeyboardButton(text='Отменить заявку', callback_data=f"confirm_upgrade:{data['id_order']}:no"))
#
#             # Отправляем сообщение на заданный вами чат или группу в Telegram
#             await bot.send_message(CHANNEL_ID, text, reply_markup=kb_chat)
#         await state.finish()
#
#
# @dp.callback_query_handler(lambda c: c.data and c.data.startswith('confirm_upgrade'), chat_id=CHANNEL_ID)
# async def agree_to_db(callback: types.CallbackQuery, state: FSMContext):
#     global conn, cursor, USER_DATA_UP
#     await bot.answer_callback_query(callback.id)
#     device, user_name, id_order, dev_name, issue, name, phone, id_client = USER_DATA_UP
#     print(USER_DATA_UP)
#     USER_DATA_UP[int(id_order)] = callback.data.split(':')[1]
#     if callback.data.split(':')[2] == 'yes':
#         try:
#             conn = sqlite3.connect('E:/sqlite3/Servigo')
#             cursor = conn.cursor()
#             # проверка на схожесть админского айди и заявителя
#             if callback.from_user.id == USER_DATA_UP[7]:
#
#                 existing_client = "SELECT id_client FROM Clients WHERE tg_username=? OR phone=?"
#                 existing_client = cursor.execute(existing_client, (user_name, phone)).fetchone()
#
#                 if existing_client:
#                     # если клиент уже существует, то используем его id_client для создания нового заказа
#                     id_client = existing_client[0]
#
#                 # вставка данных в таблицу Clients
#                 else:
#                     insert_client = "INSERT INTO Clients (id_client, tg_username,  familiya_imya, phone) VALUES (?," \
#                                     " ?, ?, ?)"
#                     cursor.execute(insert_client,
#                                    (
#                                        id_client, user_name, name, phone))
#
#                 insert_order = "INSERT INTO Orders (id_order, id_client, issue, id_status, dev_name, device_type)" \
#                                "VALUES (?, ?, ?, ?, ?, ?)"
#                 cursor.execute(insert_order, (id_order, id_client, issue, 1, 'ПК', device))
#
#                 # вставка данных в таблицу Orders
#                 conn.commit()
#                 print(f'Данные переданы для {USER_DATA_UP[7]}')
#                 await bot.send_message(USER_DATA_UP[7],
#                                        f'''Спасибо за заявку №{id_order}! В скором времени с вами свяжется менеджер.''',
#                                        reply_markup=bt_sec)
#             else:
#                 await bot.send_message(USER_DATA_UP[7], 'pizdec колбек не = юзер_дата ')
#         except sqlite3.Error as error:
#             print('Ошибка при работе с SQLite:', error)
#         finally:
#             if conn:
#                 cursor.close()
#                 conn.close()
#         time.sleep(2)
#         await main_menu(callback, state)
#         USER_DATA_UP = []
#         await state.finish()
#
#     else:
#         await bot.send_message(USER_DATA_UP[7],
#                                f'''⛔ Упс! Заявка №{id_order} была отменена.''')
#         time.sleep(2)
#         await main_menu(callback, state)
# не релизавана отправка в бд
