import sqlite3
from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.storage import FSMContextProxy
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InputFile, InlineKeyboardButton, InlineKeyboardMarkup
from back.config import CHANNEL_ID, admins
from back.form_kons import konsult
from back.form_reg import register
# from back.form_upgrade import upgrade
# from form_reg import register
from keyboards import bt_sec, kb1, bt_kat
from main import bot, dp
from texts import place, comp, virus, diag, uslugi, remont, start


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    global conn, cursor
    if message.chat.type != 'private':
        await bot.send_message(CHANNEL_ID, text='Чат бот готов к работе')
    else:
        await message.answer(
            f'''Привет, {message.from_user.username}!🖐''')
        await bot.send_photo(message.from_user.id, InputFile('Media/logo.png'), caption=start, reply_markup=bt_sec)

    try:
        conn = sqlite3.connect('E:/sqlite3/Servigo')
        cursor = conn.cursor()
        conn.execute("PRAGMA autocommit = 1")
        print(f'База подключена для {message.from_user.id}.')
    except sqlite3.Error as error:
        print('Ошибка при работе с SQLite:', error)
    finally:
        if conn:
            cursor.close()
            conn.close()



@dp.message_handler(commands=['status'], chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def update_status(message: types.Message, state: FSMContext):
    # Проверяем, что сообщение пришло из приватного чата с администратором
    #
    # if message.chat.id != CHANNEL_ID:
    #     return
    print(message.chat.id)
    # Отправляем сообщение, запрашивая номер заказа
    await message.reply("Введите номер заказа для изменения статуса:")


@dp.message_handler(chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def process_order_status(message: types.Message):
    # Получаем введенный номер заказа
    order_id = message.text.strip()

    # Проверяем, что введенный номер заказа является числом
    if not order_id.isdigit():
        await message.reply("Неверный формат номера заказа. Введите число.")
        return

    # Получаем текущий статус заказа из базы данных
    conn = sqlite3.connect('E:/sqlite3/Servigo')
    cursor = conn.cursor()
    query = "SELECT id_status FROM Orders WHERE id_order=?"
    cursor.execute(query, (order_id,))
    current_status_id = cursor.fetchone()

    # Проверяем, что заказ с указанным номером существует
    if not current_status_id:
        await message.reply(f"Заказ с номером {order_id} не найден.")
        return

    # Создаем кнопки с возможными статусами заказа
    status_buttons = [
        types.InlineKeyboardButton("Не начато", callback_data=f"status:{order_id}:1"),
        types.InlineKeyboardButton("В процессе", callback_data=f"status:{order_id}:2"),
        types.InlineKeyboardButton("Выполнено", callback_data=f"status:{order_id}:3")
    ]

    # Создаем InlineKeyboardMarkup с кнопками статусов
    status_keyboard = types.InlineKeyboardMarkup(row_width=1)
    status_keyboard.add(*status_buttons)

    # Отправляем сообщение с кнопками статусов
    await message.reply("Выберите новый статус заказа:", reply_markup=status_keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('status:'))
async def process_order_status(callback_query: types.CallbackQuery):
    # Извлекаем номер заказа и новый статус из callback query
    data = callback_query.data.split(':')
    order_id = data[1]
    new_status_id = data[2]

    # Обновляем статус заказа в базе данных
    conn = sqlite3.connect('E:/sqlite3/Servigo')
    cursor = conn.cursor()
    query = "UPDATE Orders SET id_status=? WHERE id_order=?"
    cursor.execute(query, (new_status_id, order_id))
    conn.commit()

    # Получаем информацию о пользователе
    id_client = callback_query.from_user.id
    query = "SELECT order_status FROM status WHERE id_status = ?"
    cursor.execute(query, (new_status_id,))
    status_name = cursor.fetchone()[0]
    print(id_client)
    await bot.send_message(id_client, text=f'Ваш заказ обновил свой статус: {status_name} 🌚')


@dp.callback_query_handler(text=['menu'])
async def main_menu(callback: types.CallbackQuery):
    await bot.send_message(callback.from_user.id, text='Выберите пункт меню 👇🏻', reply_markup=kb1)


@dp.message_handler(lambda message: message.text == '🔙 Назад в главное меню', state='*')
async def back_to_menu(message: types.Message):
    await bot.send_message(message.chat.id, 'Вы вернулись в главное меню', reply_markup=bt_sec)
    await bot.send_message(message.chat.id, 'Выберите пункт меню 👇🏻', reply_markup=kb1)


konsult()
register()
# upgrade()

@dp.message_handler(commands=['status'])
@dp.message_handler(text='Статус заказа')
@dp.callback_query_handler(text='order_info')
async def process_show_orders(callback_query: types.CallbackQuery):
    id_client = callback_query.from_user.id
    orders = await get_orders_for_client(id_client)  # await the coroutine
    if orders != False:
        buttons = [InlineKeyboardButton(str(order), callback_data=f"Заказ №:{order}") for order in orders]
        keyboard = InlineKeyboardMarkup(row_width=2).add(*buttons)
        await bot.send_message(id_client, "Выберите номер заказа:", reply_markup=keyboard)
    else:
        await bot.send_message(id_client, "😥 У Вас нет заказов.")


async def get_orders_for_client(id_client):
    with sqlite3.connect('E:/sqlite3/Servigo') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Orders WHERE id_client=?", (id_client,))
        count = cursor.fetchone()[0]
        if count > 0:
            cursor.execute("SELECT id_order FROM Orders WHERE id_client=?", (id_client,))
            orders = cursor.fetchall()
            return [order[0] for order in orders]
        else:
            return False  # Возвращайте пустой список, если нет заказов


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('Заказ №'))
async def process_get_data(callback_query: types.CallbackQuery):
    id_order = callback_query.data.split(':')[1]
    with sqlite3.connect('E:/sqlite3/Servigo') as conn:
        cursor = conn.cursor()
        order_tp='''UPDATE Orders
                SET total_price = (
                    SELECT SUM(s.price)
                    FROM OrderServices AS os
                    JOIN Services AS s ON os.order_id = s.id_service
                    WHERE os.order_id = ?
                )
                WHERE id_order = ?'''
        order_total = cursor.execute(order_tp, (id_order, id_order))
        print(order_total)
        order_zp = '''SELECT Orders.id_order, Clients.tg_username, Clients.familiya_imya, Clients.phone, 
                Orders.device_type, Orders.dev_name, Orders.issue, Orders.total_price, Status.order_status 
                FROM Orders 
                JOIN Clients ON Orders.id_client = Clients.id_client 
                JOIN Status ON Orders.id_status = Status.id_status 
                WHERE Orders.id_order = ?'''
        order_data = cursor.execute(order_zp, (id_order,)).fetchone()
    if order_data:
        text = f"Заявка на ремонт: {order_data[5]}:\n"
        text += f"TG user name: @{order_data[1]}\n"
        text += f"Номер заказа: {order_data[0]}\n"
        if order_data[4] != 'ПК':
            text += f"Название устройства: {order_data[5]}\n"
        text += f"Описание проблемы: {order_data[6]}\n"
        text += f"Фамилия и имя: {order_data[2]}\n"
        text += f"Телефон: {order_data[3]}\n"
        text += f"Статус заказа: {order_data[8]}\n"
        text += f"Общая стоимость: {order_data[7]} ₽"
        await bot.send_message(callback_query.from_user.id, text=text)
    else:
        await bot.send_message(callback_query.from_user.id, text="Заказ не найден")


@dp.callback_query_handler(text='my_orders')
async def process_my_orders(callback_query: types.CallbackQuery):
    await process_show_orders(callback_query)


@dp.callback_query_handler(text='all_orders')
async def process_all_orders(callback_query: types.CallbackQuery):
    # здесь можно написать код для вывода всех заказов (если это нужно)
    pass


@dp.message_handler(chat_id=CHANNEL_ID)
async def admin_reply(message: types.Message):
    if message.reply_to_message is None:
        return
    bt_info = InlineKeyboardMarkup()
    bt_info.add(InlineKeyboardButton(text='Кнопка для вопросов', callback_data='info'))
    # Парсим id из сообщения
    head = message.reply_to_message.text.split('\n')[0].split()[0]
    if head == 'Обращение':
        type = message.reply_to_message.text.split('\n')[3].split(':')[1][1:]
        if type != 'Отзыв':
            uid = message.reply_to_message.text.split('\n')[2].split()[1]
            feedback = message.reply_to_message.text.split('\n')[5]
            text = f'"{feedback}"'
            await bot.send_message(uid, f'''Вопрос: {text}
Ответ: {message.text}''', reply_markup=bt_info)

        elif type == 'Отзыв':
            await bot.send_message(CHANNEL_ID, text='Это отзыв, еблан!')

    elif head == 'Вопрос':
        uid = message.reply_to_message.text.split('\n')[1].split()[1]
        await bot.send_message(uid, f'''Ответ: {message.text}''', reply_markup=bt_info)

    elif head == 'Заявка':
        uid = message.reply_to_message.text.split('\n')[2].split()[1]
        feedback = message.reply_to_message.text.split('\n')[0].split()[3].rstrip(':')
        text = f'"{feedback}"'
        await bot.send_message(uid, f'''Ремонт {text}
Ответ: {message.text}''', reply_markup=bt_info)

    elif head == 'Модернизация':
        uid = message.reply_to_message.text.split('\n')[2].split()[1]
        await bot.send_message(uid, f'''Ваша заявка принята. А не пойти ли вам с модернизацией нахзуй?''',
                               reply_markup=bt_info)


class Form_vopros(StatesGroup):
    wait_vopros = State()
    wait_otvet = State()


@dp.callback_query_handler(text='info')
async def voprosiki(callback: types.CallbackQuery):
    await bot.send_message(callback.from_user.id, text='Введите ваш вопрос:')
    await Form_vopros.wait_vopros.set()


@dp.message_handler(state=Form_vopros.wait_vopros)
async def get_vopros(message: types.Message, state: FSMContext):
    vopros = message.text
    await state.update_data(question=vopros)  # сохраняем вопрос в состояние
    await bot.send_message(CHANNEL_ID, text=f'''Вопрос:\nTG_ID: {message.from_user.id}
Вопрос от пользователя @{message.from_user.username}:
{vopros}
    ''')
    await bot.send_message(message.from_user.id, text='Ваш вопрос отправлен администратору, ожидайте!')
    await Form_vopros.wait_otvet.set()  # переходим в состояние ожидания ответа от администратора


@dp.message_handler(state=Form_vopros.wait_otvet)
async def process_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    question = data.get('question')
    await bot.send_message(question.from_user.id, text=f'Ответ на ваш вопрос: {message.text}')
    await bot.send_message(CHANNEL_ID,
                           text=f'Ответ на вопрос от пользователя {question.from_user.id}:\n{message.text}')


# второй ответ не работает
#
async def show_services(message: types.Message):
    conn = sqlite3.connect('E:/sqlite3/Servigo')
    cursor = conn.cursor()

    # Получаем данные из таблицы Services
    query = "SELECT * FROM Services"
    cursor.execute(query)
    services = cursor.fetchall()

    # Создаем список кнопок с названиями услуг
    buttons = []
    for service in services:
        buttons.append([InlineKeyboardButton(service[1], callback_data=f'service:{service[1]}')])

    # Создаем клавиатуру с кнопками
    ser_but = InlineKeyboardMarkup(buttons)

    # Отправляем сообщение с кнопками пользователю
    await message.answer('Выберите услугу:', reply_markup=ser_but)

    conn.close()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('service:'))
async def show_service_info(callback: types.CallbackQuery):
    conn = sqlite3.connect('E:/sqlite3/Servigo')
    cursor = conn.cursor()

    # Получаем id услуги из callback_data
    service_id = callback.data.split(':')[1]

    # Получаем данные из таблицы Services по id
    query = "SELECT name, price FROM Services WHERE id_service=?"
    cursor.execute(query, (service_id,))
    service_info = cursor.fetchone()

    # Отправляем сообщение с описанием и ценой услуги
    await callback.message.answer(f'Описание: {service_info[1]}\nЦена: {service_info[3]}')

    conn.close()


@dp.callback_query_handler(text_contains='', state='*')
async def all_message(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state()
    await state.finish()
    code = callback.data
    match code:
        case 'katalog':
            await bot.send_photo(callback.from_user.id, InputFile("Media/uslugi.png"), caption=uslugi,
                                 reply_markup=bt_kat)
        case 'place':
            await bot.send_photo(callback.from_user.id, InputFile("Media/map.PNG"), caption=place, reply_markup=bt_sec)
            await bot.send_location(callback.from_user.id, 55.544813, 37.516697, 'Сервиго', 'Москва')
            # time.sleep(1)
            # await main_menu(callback)
        case 'company':
            await bot.send_photo(callback.from_user.id, InputFile("Media/gorshok.jpg"), caption=comp,
                                 reply_markup=bt_sec, )

            # time.sleep(1)
            # await main_menu(callback)


# Вывод значений таблицы Sevices для ознакомления


@dp.message_handler(text_contains='', state='*')
async def kat_info(message: types.Message, state: FSMContext):
    await state.set_state()
    await state.finish()
    code = message.text
    bt_reg = InlineKeyboardMarkup()
    bt_reg.add(InlineKeyboardButton(text='Оставить заявку', callback_data='register'))
    bt_uprgade = InlineKeyboardMarkup()
    bt_uprgade.add(InlineKeyboardButton(text='Оставить заявку на апгрейд', callback_data='upgrade'))
    match code:
        case '₽ Наши цены ₽':
            await bot.send_document(message.from_user.id, InputFile('Media/pricelist.png'))
        case '🛠 Ремонт':
            await bot.send_photo(message.from_user.id, InputFile('Media/remont.jpg'), caption=remont,
                                 reply_markup=bt_reg)
            # await show_services(message)
        case '💉 Диагностика и профилактика':
            await bot.send_photo(message.from_user.id, InputFile('Media/diag.jpg'), caption=diag, reply_markup=bt_reg)
        case '📈 Апгрейд ПК':
            await bot.send_message(message.from_user.id, text='Ну тут нужно чекать в ДНС цены.',
                                   reply_markup=bt_uprgade)
        # case 'Удаление вирусов':
        #     await bot.send_photo(message.from_user.id, InputFile("Media/virus.jpg"), caption=virus)
        # case 'Если просто не включается компьютер?':
        #     await bot.send_message(message.from_user.id,
        #                            text='А может ну его... Компы эти сложные, а?\n и кстати, не пишите сюда больше')
        #     await bot.send_message(message.from_user.id, text='Бан по причине тупоголовый')
        case '🖥 ➕ 🎮 Сборка':
            await bot.send_message(message.from_user.id,
                                   text='Привозите свои комплектующие. Мы поможем вам собрать ПК! ')

# @dp.message_handler(commands=['/orders'])
# async def show_orders(message: types.Message):
#     # Проверяем, что сообщение пришло из админ-чата
#     if message.chat.id != CHANNEL_ID:
#         return
#
#     # Подключаемся к базе данных
#     conn = sqlite3.connect('E:/sqlite3/Servigo')
#     cursor = conn.cursor()
#
#     # Получаем все заказы из таблицы Orders
#     query = "SELECT * FROM Orders"
#     cursor.execute(query)
#     orders = cursor.fetchall()
#
#     # Создаем список кнопок с возможными статусами
#     status_buttons = []
#     query = "SELECT * FROM status"
#     cursor.execute(query)
#     statuses = cursor.fetchall()
#     for status in statuses:
#         status_buttons.append([types.InlineKeyboardButton(status[1], callback_data=f'status:{status[0]}')])
#
#     # Создаем кнопку "назад"
#     back_button = types.InlineKeyboardButton('Назад', callback_data='back')
#
#     # Создаем InlineKeyboardMarkup с кнопками статусов и кнопкой "назад"
#     status_keyboard = types.InlineKeyboardMarkup(status_buttons)
#     status_keyboard.add(back_button)
#
#     # Отправляем сообщение с заказами и кнопками статусов
#     for order in orders:
#         status_id = order[5]
#         query = "SELECT name FROM status WHERE id_status=?"
#         cursor.execute(query, (status_id,))
#         status_name = cursor.fetchone()[0]
#         status_text = f'Статус: {status_name}\n'
#         order_text = f'{order[1]} {order[2]} ({order[3]})\n{order[4]}\n{status_text}'
#         await message.reply(order_text, reply_markup=status_keyboard)
#
#     # Закрываем соединение с базой данных
#     conn.close()
#
#
# # Обрабатываем нажатия на кнопки статусов
# @dp.callback_query_handler(lambda c: c.data and c.data.startswith('status:'))
# async def change_order_status(callback: types.CallbackQuery):
#     # Проверяем, что сообщение пришло из админ-чата
#     if callback.message.chat.id != CHANNEL_ID:
#         return
#
#     # Получаем id заказа и id статуса из callback_data
#     order_id = callback.message.text.split('\n')[0]
#     status_id = int(callback.data.split(':')[1])
#
#     # Подключаемся к базе данных
#     conn = sqlite3.connect('E:/sqlite3/Servigo')
#     cursor = conn.cursor()
#
#     # Обновляем статус заказа в таблице Orders
#     query = "UPDATE Orders SET id_status=? WHERE id=?"
#     cursor.execute(query, (status_id, order_id))
#     conn.commit()
#
#     # Получаем имя статуса из таблицы status
#     query = "SELECT name FROM status WHERE id_status=?"
#     cursor.execute(query, (status_id,))
#     status_name = cursor.fetchone()[0]
#
#     # Отправляем сообщение об успешном обновлении статуса
#     await callback.answer(f'Статус заказа изменен на "{status_name}"')
#
#     # Закрываем соединение с базой данных
#     conn.close()
#
#     # После обновления статуса заказа, отправляем обновленный список заказов с кнопками статусов
#     await show_orders(callback.message)


# Обрабатываем нажатие на кнопку "Назад"
# @dp.callback_query_handler(lambda c: c.data == 'back')
# async def back_to_orders(callback: types.CallbackQuery):
#     # Проверяем, что сообщение пришло из админ-чата
#     if callback.message.chat.id != CHANNEL_ID:
#         return
#     # После нажатия на кнопку "назад", отправляем список заказов с кнопками статусов
#     await show_orders(callback.message)
