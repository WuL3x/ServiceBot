import sqlite3

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from back.config import CHANNEL_ID
from back.main import bot, dp


class StatusForm(StatesGroup):
    order_id = State()
    new_status = State()


@dp.message_handler(commands=['status'], chat_id=CHANNEL_ID)
async def update_status(message: types.Message):
    # Проверяем, что сообщение пришло из приватного чата с администратором

    # Отправляем сообщение, запрашивая номер заказа
    await message.reply("Введите номер заказа для изменения статуса:")

    # Переходим в состояние ожидания номера заказа
    await StatusForm.order_id.set()


@dp.message_handler(state=StatusForm.order_id, chat_id=CHANNEL_ID)
async def process_order_id(message: types.Message, state: FSMContext):
    # Получаем введенный номер заказа
    order_id = message.text.strip()

    # Проверяем, что введенный номер заказа является числом
    if not order_id.isdigit():
        await message.reply("Неверный формат номера заказа. Введите число.")
        return

    # Сохраняем номер заказа в состоянии
    await state.update_data(order_id=order_id)

    # Переходим в состояние ожидания нового статуса
    await StatusForm.new_status.set()

    # Создаем кнопки с возможными статусами заказа
    status_buttons = [
        types.InlineKeyboardButton("Не начато", callback_data="status:1"),
        types.InlineKeyboardButton("В процессе", callback_data="status:2"),
        types.InlineKeyboardButton("Выполнено", callback_data="status:3")
    ]

    # Создаем InlineKeyboardMarkup с кнопками статусов
    status_keyboard = types.InlineKeyboardMarkup(row_width=1)
    status_keyboard.add(*status_buttons)

    # Отправляем сообщение с кнопками статусов
    await message.reply("Выберите новый статус заказа:", reply_markup=status_keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('status:'),
                           state=StatusForm.new_status, chat_id=CHANNEL_ID)
async def process_order_status(callback_query: types.CallbackQuery, state: FSMContext):
    # Извлекаем новый статус из callback query
    new_status_id = callback_query.data.split(':')[1]

    # Получаем сохраненный в состоянии номер заказа
    data = await state.get_data()
    order_id = data.get('order_id')

    # Обновляем статус заказа в базе данных
    conn = sqlite3.connect('E:/sqlite3/Servigo')
    cursor = conn.cursor()
    query = "UPDATE Orders SET id_status=? WHERE id_order=?"
    cursor.execute(query, (new_status_id, order_id))
    conn.commit()

    # Получаем информацию о пользователе
    que_id_client = "SELECT id_client FROM orders WHERE id_order=?"
    cursor.execute(que_id_client, (order_id,))
    id_client = cursor.fetchone()[0]
    query = "SELECT order_status FROM status WHERE id_status = ?"
    cursor.execute(query, (new_status_id,))
    status_name = cursor.fetchone()[0]

    # Отправляем сообщение пользователю
    await bot.send_message(id_client, text=f'Ваш заказ обновил свой статус: {status_name} 🌚')

    # Возвращаемся в начальное состояние
    await state.finish()
