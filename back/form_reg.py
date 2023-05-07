import logging
import time
import uuid
import sqlite3
import json
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from back.keyboards import kb_dev, kb1
from config import CHANNEL_ID
from keyboards import bt_sec
from main import bot, dp

button_cancel = types.InlineKeyboardButton('Отмена', callback_data='cancel')
cancelButton = types.ReplyKeyboardMarkup(resize_keyboard=True).add(button_cancel)
USER_DATA = {}



@dp.callback_query_handler(text=['Меню'])
async def main_menu(callback: types.callback_query):
    await bot.send_message(callback.from_user.id, reply_markup=kb1, text='Выберите пункт меню 👇🏻')


def register():
    class RepairForm(StatesGroup):
        device = State()  # выбор типа устройства
        dev_name = State()
        issue = State()
        name = State()
        phone = State()
        confirm = State()
        dbconn = State()

    @dp.callback_query_handler(text='register')
    @dp.message_handler(text='Оставить заявку на ремонт')
    async def register_order(callback: types.callback_query, state: FSMContext):
        await bot.send_message(callback.from_user.id,
                               f'''{callback.from_user.username}, мы просим Вас указывать полную информацию об 
устройстве и описывать проблему максимально развернуто''',
                               reply_markup=cancelButton)
        async with state.proxy() as data:
            data['user_name'] = callback.from_user.username
            data['id_order'] = str(uuid.uuid4().int)[:6]
            data['id_client'] = callback.from_user.id
            await state.update_data(data)
        await bot.send_message(callback.from_user.id, 'Выберите тип устройства:', reply_markup=kb_dev)
        await RepairForm.device.set()

    @dp.message_handler(state='*', commands='cancel')
    @dp.message_handler(Text(equals='Отмена', ignore_case=True), state='*')
    async def cancel(message: types.message, state: FSMContext):
        current_state = await state.get_state()
        if current_state is None:
            return

        await bot.send_message(message.from_user.id, text='''Отмена отправки⛔''', reply_markup=bt_sec)
        time.sleep(1)
        await main_menu(message)
        await state.finish()

    @dp.callback_query_handler(lambda c: c.data.startswith('device:'), state=RepairForm.device)
    async def process_device(callback: types.CallbackQuery, state: FSMContext):
        data = callback.data.split(':')
        device = data[1]
        # сохраняем данные в состоянии
        await state.update_data(device=device)

        if device == 'ПК':
            await bot.send_message(callback.from_user.id,
                                   "Пожалуйста, укажите что произошло с ПК.",
                                   reply_markup=cancelButton)
            await RepairForm.issue.set()

        else:
            await bot.send_message(callback.from_user.id,
                                   "Пожалуйста, напишите полное название устройства. ",
                                   reply_markup=cancelButton)
            await RepairForm.dev_name.set()

    @dp.message_handler(state=RepairForm.dev_name)
    async def process_dev_name(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['dev_name'] = message.text
            await state.update_data(data)
        await bot.send_message(message.from_user.id, "Пожалуйста, опишите проблему.", reply_markup=cancelButton)
        await RepairForm.issue.set()

    @dp.message_handler(state=RepairForm.issue)
    async def process_issue(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['issue'] = message.text
            await state.update_data(data)

        await message.reply("Введите Ваши фамилию и имя.", reply=False, reply_markup=cancelButton)
        await RepairForm.name.set()

    @dp.message_handler(state=RepairForm.name)
    async def process_name(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['name'] = message.text

        await message.reply("Введите Ваш номер телефона.", reply=False, reply_markup=cancelButton)
        await RepairForm.phone.set()

    @dp.message_handler(state=RepairForm.phone)
    async def process_phone(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['phone'] = message.text
            await state.update_data(data)

            # формируем сообщение
            text = f"Заявка\n"
            text += f"Ремонт {data['device']}а:\n"
            text += f"Номер заявки: {data['id_order']}\n"
            if data['device'] != 'ПК':
                text += f"Название устройства: {data['dev_name']}\n"
            text += f"Описание проблемы: {data['issue']}\n"
            text += f"Имя: {data['name']}\n"
            text += f"Телефон: {data['phone']}\n"

            kb_con = types.InlineKeyboardMarkup()
            kb_con.insert(types.InlineKeyboardButton(text="Все верно", callback_data='confirm:verno'))
            kb_con.add(types.InlineKeyboardButton(text="Нет. Есть ошибка", callback_data='confirm:error'))

            # отправляем сообщение пользователю
            await bot.send_message(chat_id=message.from_user.id, text=text, parse_mode=ParseMode.HTML,
                                   reply_markup=kb_con)
        logging.debug(f"Processing callback query with state {await state.get_state()}")

        await state.get_state()
        await RepairForm.confirm.set()

    @dp.callback_query_handler(state=RepairForm.confirm)
    async def process_confirm(callback: types.CallbackQuery, state: FSMContext):
        # обрабатываем ответ на кнопку
        global USER_DATA
        if callback.data.split(':')[1] == 'error':
            reank = types.InlineKeyboardMarkup()
            reank.insert(types.InlineKeyboardButton(text="Оставить заявку", callback_data="register"))
            await bot.send_message(callback.from_user.id, "Извините, пожалуйста, пройдите опрос снова",
                                   reply_markup=reank)
            async with state.proxy() as data:
                data['user_name'] = callback.from_user.first_name
                data['id_order'] = data['id_order']

        elif callback.data.split(':')[1] == 'verno':
            await bot.send_message(callback.from_user.id,
                                   "Спасибо за заявку! В скором времени с вами свяжется менеджер",
                                   reply_markup=bt_sec)
            async with state.proxy() as data:
                text = f"Заявка на ремонт: {data['device']}:\n"
                text += f"TG user name: @{data['user_name']}\n"
                text += f"TG_ID: {data['id_client']}\n"
                text += f"Номер заявки: {data['id_order']}\n"
                if data['device'] != 'ПК':
                    text += f"Название устройства: {data['dev_name']}\n"
                else:
                    data['dev_name'] = 'ПК'
                text += f"Описание проблемы: {data['issue']}\n"
                text += f"Фамилия и имя: {data['name']}\n"
                text += f"Телефон: {data['phone']}\n"
            logging.debug(f"Processing callback query with state {await state.get_state()}")
            USER_DATA = [data['device'], data['user_name'], data['id_order'], data['dev_name'], data['issue'],
                         data['name'], data['phone'], data['id_client']]

            kb_chat = InlineKeyboardMarkup()
            kb_chat.add(InlineKeyboardButton(text="Перейти в чат",
                                             url=f"t.me/{callback.from_user.username}"))
            kb_chat.add(InlineKeyboardButton(text='Подтвердить заявку', callback_data='agree:yes'))
            kb_chat.add(InlineKeyboardButton(text='Отменить заявку', callback_data='agrer:no'))

            # Отправляем сообщение на заданный вами чат или группу в Telegram
            await bot.send_message(CHANNEL_ID, text, reply_markup=kb_chat)
        await RepairForm.dbconn.set()


@dp.callback_query_handler(lambda callback_query: True, chat_id=CHANNEL_ID)
async def agree_to_db(callback: types.CallbackQuery, state: FSMContext):
    global conn, cursor, USER_DATA
    await bot.answer_callback_query(callback.id)
    device, user_name, id_order, dev_name, issue, name, phone, id_client = USER_DATA
    if callback.data.split(':')[1] == 'yes':
        try:
            conn = sqlite3.connect('E:/sqlite3/Servigo')
            cursor = conn.cursor()
            tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
            print(tables)

            # вставка данных в таблицу Clients
            id_device_type = cursor.execute(
                f"SELECT id_device from Device_type dt WHERE name == '{device}'").fetchone()[0]

            print(id_device_type)
            if device == 'ПК':
                insert_client_query = "INSERT INTO Clients (tg_username, model, device_type, familiya_imya, phone, " \
                                      "id_device_type) VALUES (?, ?, ?, ?, ?, ?)"
                cursor.execute(insert_client_query,
                               (user_name, 'ПК', device, name, phone,
                                id_device_type))

            else:
                insert_client_query = "INSERT INTO Clients (tg_username, model, device_type, familiya_imya, phone, " \
                                      "id_device_type) VALUES (?, ?, ?, ?, ?, ?)"
                cursor.execute(insert_client_query,
                               (
                                   user_name, dev_name, device, name,
                                   phone,
                                   id_device_type))

            # вставка данных в таблицу Orders
            insert_order_query = "INSERT INTO Orders (id_order, id_client, issue, id_status) VALUES (?, ?, ?, ?)"
            cursor.execute(insert_order_query, (id_order, id_client, issue, 0))

            conn.commit()
            print('Данные переданы')
            await bot.send_message(callback.from_user.id,
                                   f'''Спасибо за заявку №{id_order}! В скором времени с вами свяжется менеджер.''',
                                   reply_markup=bt_sec)
        except sqlite3.Error as error:
            print('Ошибка при работе с SQLite:', error)
        finally:
            if conn:
                cursor.close()
                conn.close()
        USER_DATA = []
        await state.finish()
    else:
        await bot.send_message(callback.from_user.id,
                               f'''⛔ Упс! Заявка №{id_order} была отменена.''')
        time.sleep(2)
        await main_menu(callback)

    # @dp.callback_query_handler(state=RepairForm.dbconn)
    # async def agree_to_db(callback: types.CallbackQuery, state: FSMContext):
    #     global conn, cursor
    #     async with state.proxy() as data:
    #         if callback.data.split(':')[1] == 'yes':
    #             print(data)
    #             try:
    #                 conn = sqlite3.connect('E:/sqlite3/Servigo')
    #                 cursor = conn.cursor()
    #                 tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    #                 print(tables)
    #
    #                 # вставка данных в таблицу Clients
    #                 id_device_type = cursor.execute(
    #                     f"SELECT id_device from Device_type dt WHERE name == '{data['device']}'").fetchone()[0]
    #
    #                 print(id_device_type)
    #                 if data['device'] == 'ПК':
    #                     insert_client_query = "INSERT INTO Clients (tg_username, model, device_type, familiya_imya, phone, " \
    #                                           "id_device_type) VALUES (?, ?, ?, ?, ?, ?)"
    #                     cursor.execute(insert_client_query,
    #                                    (data['user_name'], 'ПК', data['device'], data['name'], data['phone'], id_device_type))
    #
    #                 else:
    #                     insert_client_query = "INSERT INTO Clients (tg_username, model, device_type, familiya_imya, phone, " \
    #                                           "id_device_type) VALUES (?, ?, ?, ?, ?, ?)"
    #                     cursor.execute(insert_client_query,
    #                                    (
    #                                        data['user_name'], data['dev_name'], data['device'], data['name'],
    #                                        data['phone'],
    #                                        id_device_type))
    #
    #                 # вставка данных в таблицу Orders
    #                 insert_order_query = "INSERT INTO Orders (id_order, id_client, issue, id_status) VALUES (?, ?, ?, ?)"
    #                 cursor.execute(insert_order_query, (data['id_order'], data['id_client'], data['issue'], 0))
    #
    #                 conn.commit()
    #                 print('Данные переданы')
    #                 await bot.send_message(callback.from_user.id,
    #                                        "Спасибо за заявку! В скором времени с вами свяжется менеджер",
    #                                        reply_markup=bt_sec)
    #             except sqlite3.Error as error:
    #                 print('Ошибка при работе с SQLite:', error)
    #             finally:
    #                 if conn:
    #                     cursor.close()
    #                     conn.close()
    #     await state.finish()

# @dp.callback_query_handler(text='agree', chat_id=CHANNEL_ID, state=RepairForm.dbconn)
# async def order_agree(callback: types.CallbackQuery, state: FSMContext):
#     global conn, cursor
#     print("Button clicked!")
#     data = await state.get_data()
#     print(data)
#     try:
#         conn = sqlite3.connect('E:/sqlite3/Servigo')
#         cursor = conn.cursor()
#         tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
#         print(tables)
#
#         # вставка данных в таблицу Clients
#         id_device_type = cursor.execute(
#             f"SELECT id_device from Device_type dt WHERE name == '{data['device']}'").fetchone()[0]
#
#         print(id_device_type)
#         if data['device'] == 'ПК':
#             insert_client_query = "INSERT INTO Clients (tg_username, model, device_type, familiya_imya, phone, " \
#                                   "id_device_type) VALUES (?, ?, ?, ?, ?, ?)"
#             cursor.execute(insert_client_query,
#                            (data['user_name'], 'ПК', data['device'], data['name'], data['phone'],
#                             id_device_type))
#
#         else:
#             insert_client_query = "INSERT INTO Clients (tg_username, model, device_type, familiya_imya, phone, " \
#                                   "id_device_type) VALUES (?, ?, ?, ?, ?, ?)"
#             cursor.execute(insert_client_query,
#                            (
#                                data['user_name'], data['dev_name'], data['device'], data['name'],
#                                data['phone'],
#                                id_device_type))
#
#         # вставка данных в таблицу Orders
#         insert_order_query = "INSERT INTO Orders (id_order, id_client, issue, id_status) VALUES (?, ?, ?, ?)"
#         cursor.execute(insert_order_query, (data['id_order'], data['id_client'], data['issue'], 0))
#
#         conn.commit()
#         print('Данные переданы')
#         await bot.send_message(callback.from_user.id,
#                                "Спасибо за заявку! В скором времени с вами свяжется менеджер",
#                                reply_markup=bt_sec)
#     except sqlite3.Error as error:
#         print('Ошибка при работе с SQLite:', error)
#     finally:
#         if conn:
#             cursor.close()
#             conn.close()
#     await state.finish()
#
# @dp.callback_query_handler(text='refuse')
# async def order_refuse(callback: types.CallbackQuery):
#     bot.send_message(callback.from_user.id, 'Вам отказали')

# @dp.callback_query_handler(text='agree', state=RepairForm.confirm)
# async def dbconnection(callback: types.CallbackQuery, state: FSMContext):
#     global conn, cursor
#     try:
#         conn = sqlite3.connect('E:/sqlite3/Servigo')
#         cursor = conn.cursor()
#         tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
#         print(tables)
#         async with state.proxy() as data:
#             data = await state.get_data()
#             # вставка данных в таблицу Clients
#             print(data['device'])
#             id_device_type = cursor.execute(
#                     f"SELECT id_device from Device_type dt where name == '{data['device']}'").fetchone()[0]
#             print(id_device_type)
#             if data['device'] == 'ПК':
#                 insert_client_query = "INSERT INTO Clients (tg_username, model, device_type, familiya_imya, phone, " \
#                                       "id_device_type) VALUES (?, ?, ?, ?, ?, ?)"
#                 cursor.execute(insert_client_query,
#                                (data['user_name'], 'ПК', data['device'], data['name'], data['phone'],
#                                 id_device_type))
#
#             else:
#                 insert_client_query = "INSERT INTO Clients (tg_username, model, device_type, familiya_imya, phone, " \
#                                       "id_device_type) VALUES (?, ?, ?, ?, ?, ?)"
#                 cursor.execute(insert_client_query,
#                                (
#                                    data['user_name'], data['dev_name'], data['device'], data['name'],
#                                    data['phone'],
#                                    id_device_type))
#
#             # вставка данных в таблицу Orders
#             insert_order_query = "INSERT INTO Orders (id_order, id_client, issue, id_status) VALUES (?, ?, ?, ?)"
#             cursor.execute(insert_order_query, (data['id_order'], data['id_client'], data['issue'], 0))
#
#             conn.commit()
#             print('Данные переданы')
#     except sqlite3.Error as error:
#         print('Ошибка при работе с SQLite:', error)
#     finally:
#         if conn:
#             cursor.close()
#             conn.close()
