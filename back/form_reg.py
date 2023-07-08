import logging
import time

import sqlite3
import re

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from back.keyboards import kb_dev
from config import CHANNEL_ID
from keyboards import bt_sec
from main import bot, dp, generate_order_id

button_cancel = types.InlineKeyboardButton('Отмена', callback_data='cancel')
cancelButton = types.ReplyKeyboardMarkup(resize_keyboard=True).add(button_cancel)
USER_DATA = {}


@dp.callback_query_handler(text=['Меню'])
async def main_menu(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if data.get('user_id') == callback.from_user.id:
            await main_menu(callback)
        else:
            await callback.answer(text='Вы не заполняете форму')


def register():
    class RepairForm(StatesGroup):
        device = State()  # выбор типа устройства
        dev_name = State()
        issue = State()
        name = State()
        phone = State()
        confirm = State()


    @dp.message_handler(commands=['register'])
    @dp.callback_query_handler(text='register')
    @dp.message_handler(text='Оставить заявку на ремонт')
    async def register_order(callback: types.callback_query, state: FSMContext):
        await bot.send_message(callback.from_user.id,
                               f'''{callback.from_user.username}, мы просим Вас указывать полную информацию об 
устройстве и описывать проблему максимально развернуто''',
                               reply_markup=cancelButton)
        async with state.proxy() as data:
            data['user_name'] = callback.from_user.username
            data['id_order'] = generate_order_id()
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
        full_name = message.text.strip()
        # Проверяем, что фамилия и имя начинаются с заглавной буквы
        if not full_name.istitle():
            await message.reply(
                "Фамилия и имя должны начинаться с заглавной буквы. Пожалуйста, введите правильные данные.")
            return
        async with state.proxy() as data:
            data['name'] = full_name
            await state.update_data(data)
        phone_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        share = KeyboardButton(text="Отправить контакт", request_contact=True)
        phone_keyboard.add(share).row(button_cancel)
        await message.answer("Пожалуйста, отправьте свой контактный номер телефона или введите его вручную",
                             reply_markup=phone_keyboard)
        await RepairForm.next()

    @dp.message_handler(state=RepairForm.phone, content_types=[types.ContentType.TEXT, types.ContentType.CONTACT])
    async def process_phone(message: types.Message, state: FSMContext):
        if message.contact:
            phone = message.contact.phone_number
        else:
            phone = message.text.strip()

            # Проверяем, что номер телефона соответствует шаблону "+79123456789"
            if not re.match(r"\+\d{11}", phone):
                await message.reply(
                    "Номер телефона должен начинаться с +7. Пожалуйста, введите правильный номер.")
                return

        async with state.proxy() as data:
            data['phone'] = phone
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
            await bot.send_message(callback.from_user.id,
                                   f'''Спасибо за заявку! В скором времени мы ее рассмотрим.''',
                                   reply_markup=bt_sec)

            kb_chat = InlineKeyboardMarkup()
            kb_chat.add(InlineKeyboardButton(text="Перейти в чат",
                                             url=f"t.me/{callback.from_user.username}"))
            kb_chat.add(
                InlineKeyboardButton(text='Подтвердить заявку', callback_data=f"confirm_order:{data['id_order']}:yes"))
            kb_chat.add(
                InlineKeyboardButton(text='Отменить заявку', callback_data=f"confirm_order:{data['id_order']}:no"))

            # Отправляем сообщение на заданный вами чат или группу в Telegram
            await bot.send_message(CHANNEL_ID, text, reply_markup=kb_chat)
        await state.finish()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('confirm_order'), chat_id=CHANNEL_ID)
async def agree_to_db(callback: types.CallbackQuery, state: FSMContext):
    global conn, cursor, USER_DATA
    await bot.answer_callback_query(callback.id)
    device, user_name, id_order, dev_name, issue, name, phone, id_client = USER_DATA
    print(USER_DATA)
    USER_DATA[int(id_order)] = callback.data.split(':')[1]
    if callback.data.split(':')[2] == 'yes':
        try:
            conn = sqlite3.connect('E:/sqlite3/Servigo')
            cursor = conn.cursor()
            # проверка на схожесть админского айди и заявителя
            if callback.from_user.id != USER_DATA[7]:

                existing_client = "SELECT id_client FROM Clients WHERE tg_username=? OR phone=?"
                existing_client = cursor.execute(existing_client, (user_name, phone)).fetchone()

                if existing_client:
                    # если клиент уже существует, то используем его id_client для создания нового заказа
                    id_client = existing_client[0]

                # вставка данных в таблицу Clients
                else:
                    insert_client = "INSERT INTO Clients (id_client, tg_username,  familiya_imya, phone) VALUES (?," \
                                    " ?, ?, ?)"
                    cursor.execute(insert_client,
                                   (
                                       id_client, user_name, name, phone))

                if device == 'ПК':
                    insert_order = "INSERT INTO Orders (id_order, id_client, issue, id_status, dev_name, device_type)" \
                                   "VALUES (?, ?, ?, ?, ?, ?)"
                    cursor.execute(insert_order, (id_order, id_client, issue, 1, 'ПК', device))

                else:
                    insert_client = "INSERT INTO Orders (id_order, id_client, issue, id_status, dev_name, device_type)" \
                                    "VALUES (?, ?, ?, ?, ?, ?)"
                    cursor.execute(insert_client,
                                   (
                                       id_order, id_client, issue, 1, dev_name, device))

                # вставка данных в таблицу Orders
                conn.commit()
                print(f'Данные переданы для {USER_DATA[7]}')
                await bot.send_message(USER_DATA[7],
                                       f'''Спасибо за заявку №{id_order}! В скором времени с вами свяжется менеджер.''',
                                       reply_markup=bt_sec)
            else:
                await bot.send_message(USER_DATA[7], 'Ошибка доступа')
                await main_menu(callback, state)
        except sqlite3.Error as error:
            print('Ошибка при работе с SQLite:', error)
        finally:
            if conn:
                cursor.close()
                conn.close()
        time.sleep(2)
        await main_menu(callback, state)
        USER_DATA = []
        await state.finish()

    else:
        await bot.send_message(USER_DATA[7],
                               f'''⛔ Упс! Заявка №{id_order} была отменена.''')
        time.sleep(2)
        await main_menu(callback,state)

