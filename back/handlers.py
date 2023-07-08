import sqlite3

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InputFile, InlineKeyboardButton, InlineKeyboardMarkup

from back.config import CHANNEL_ID
from back.form_kons import konsult
from back.form_reg import register
from back.status_act import StatusForm, update_status, process_order_id, process_order_status
# from back.form_upgrade import upgrade
# from form_reg import register
from keyboards import bt_sec, kb1, bt_kat
from main import bot, dp
from texts import place, comp, diag, uslugi, remont, start


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


@dp.callback_query_handler(text=['menu'])
async def main_menu(callback: types.CallbackQuery):
    await bot.send_message(callback.from_user.id, text='Выберите пункт меню 👇🏻', reply_markup=kb1)


@dp.message_handler(lambda message: message.text == '🔙 Назад в главное меню', state='*')
async def back_to_menu(message: types.Message):
    await bot.send_message(message.chat.id, 'Вы вернулись в главное меню', reply_markup=bt_sec)
    await bot.send_message(message.chat.id, 'Выберите пункт меню 👇🏻', reply_markup=kb1)


konsult()
register()

dp.register_message_handler(update_status, commands=['status'], chat_id=CHANNEL_ID)
dp.register_message_handler(process_order_id, state=StatusForm.order_id, chat_id=CHANNEL_ID)
dp.register_callback_query_handler(process_order_status,
                                   lambda callback_query: callback_query.data.startswith('status:'),
                                   state=StatusForm.new_status, chat_id=CHANNEL_ID)


@dp.message_handler(commands=['status'])
@dp.message_handler(text='Статус заказа')
@dp.callback_query_handler(text='order_info')
async def status_start(callback: types.CallbackQuery):
    await show_orders(callback)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('Заказ №'))
async def status_get_data(callback_query: types.CallbackQuery):
    id_order = callback_query.data.split(':')[1]
    with sqlite3.connect('E:/sqlite3/Servigo') as conn:
        cursor = conn.cursor()
        cursor.execute('''UPDATE Orders
                SET total_price = (
                    SELECT SUM(s.price)
                    FROM OrderServices AS os
                    JOIN Services AS s ON os.order_id = s.id_service
                    WHERE os.order_id = ?
                )
                WHERE id_order = ?''', (id_order, id_order))
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
        conn.close()


async def show_orders(callback):
    id_client = callback.from_user.id
    orders = await orders_for_client(id_client)  # await the coroutine
    if orders:
        if isinstance(orders, list):
            buttons = [InlineKeyboardButton(str(order), callback_data=f"Заказ №:{order}") for order in orders]
            keyboard = InlineKeyboardMarkup(row_width=2).add(*buttons)
            await bot.send_message(id_client, "Выберите номер заказа:", reply_markup=keyboard)
        else:
            await send_order_info(id_client, orders)
    else:
        await bot.send_message(id_client, "😥 У Вас нет заказов.")


async def orders_for_client(id_client):
    with sqlite3.connect('E:/sqlite3/Servigo') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Orders WHERE id_client=?", (id_client,))
        count = cursor.fetchone()[0]
        if count > 0:
            cursor.execute("SELECT id_order FROM Orders WHERE id_client=?", (id_client,))
            orders = cursor.fetchall()
            if count > 1:
                return [order[0] for order in orders]
            else:
                return orders[0][0]
        else:
            return False  # Возвращайте пустой список, если нет заказов


async def send_order_info(id_client, order_id):
    with sqlite3.connect('E:/sqlite3/Servigo') as conn:
        cursor = conn.cursor()
        cursor.execute('''UPDATE Orders
                SET total_price = (
                    SELECT SUM(s.price)
                    FROM OrderServices AS os
                    JOIN Services AS s ON os.service_id = s.id_service
                    WHERE os.order_id = ?
                )
                WHERE id_order = ?''', (order_id, order_id))
        order_zp = '''SELECT Orders.id_order, Clients.tg_username, Clients.familiya_imya, Clients.phone, 
                Orders.device_type, Orders.dev_name, Orders.issue, Orders.total_price, Status.order_status 
                FROM Orders 
                JOIN Clients ON Orders.id_client = Clients.id_client 
                JOIN Status ON Orders.id_status = Status.id_status 
                WHERE Orders.id_order = ?'''
        order_data = cursor.execute(order_zp, (order_id,)).fetchone()
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
        await bot.send_message(id_client, text=text)
    else:
        await bot.send_message(id_client, text="Заказ не найден")


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
    await bot.send_message(message.from_user.id, text=f'Ответ на ваш вопрос: {message.text}')
    await bot.send_message(CHANNEL_ID,
                           text=f'Ответ на вопрос от пользователя {message.from_user.id}:\n{message.text}')


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
            await bot.send_message(message.from_user.id, text='На данный момент услуга не доступна',
                                   reply_markup=bt_uprgade)
        case '🖥 ➕ 🎮 Сборка':
            await bot.send_message(message.from_user.id,
                                   text='Привозите свои комплектующие. Мы поможем вам собрать ПК! ')


