import re
import time
import json
import pickle
import sqlite3
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import state
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InputFile, WebAppInfo, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.exceptions import CantInitiateConversation

from back.config import CHANNEL_ID
from back.form_kons import konsult
from back.form_reg import register
from back.form_upgrade import upgrade

# from form_reg import register
from keyboards import bt_sec, kb1, bt_kat
from main import bot, dp
from texts import place, comp, virus, diag, uslugi, remont, start


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    global conn, cursor
    await message.answer(
        f'''Привет, {message.from_user.username}!🖐''')
    await bot.send_photo(message.from_user.id, InputFile('Photo/logo.png'), caption=start, reply_markup=bt_sec)
    # time.sleep(1)
    # await main_menu(message)

    try:
        conn = sqlite3.connect('E:/sqlite3/Servigo')
        cursor = conn.cursor()
        conn.execute("PRAGMA autocommit = 1")
        print('База подключена')
    except sqlite3.Error as error:
        print('Ошибка при работе с SQLite:', error)
    finally:
        if conn:
            cursor.close()
            conn.close()


@dp.callback_query_handler(text=['menu'])
async def main_menu(callback: types.callback_query):
    await bot.send_message(callback.from_user.id, text='Выберите пункт меню 👇🏻', reply_markup=kb1)


@dp.message_handler(lambda message: message.text == 'Назад в главное меню', state='*')
async def back_to_menu(message: types.Message):
    await bot.send_message(message.chat.id, 'Вы вернулись в главное меню', reply_markup=bt_sec)
    await bot.send_message(message.chat.id, 'Выберите пункт меню 👇🏻', reply_markup=kb1)


konsult()
register()
upgrade()


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
        await bot.send_message(uid, f'''Ваша заявка принята.''', reply_markup=bt_info)


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

@dp.callback_query_handler(text_contains='', state='*')
async def all_message(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state()
    await state.finish()
    code = callback.data
    match code:
        case 'katalog':
            await bot.send_photo(callback.from_user.id, InputFile("Photo/uslugi.png"), caption=uslugi,
                                 reply_markup=bt_kat)
        case 'place':
            await bot.send_photo(callback.from_user.id, InputFile("Photo/map.PNG"), caption=place, reply_markup=bt_sec)
            await bot.send_location(callback.from_user.id, 55.544813, 37.516697, 'Сервиго', 'Москва')
            # time.sleep(1)
            # await main_menu(callback)
        case 'company':
            await bot.send_photo(callback.from_user.id, InputFile("Photo/gorshok.jpg"), caption=comp,
                                 reply_markup=bt_sec, )

            # time.sleep(1)
            # await main_menu(callback)


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
        case 'Ремонт':
            await bot.send_photo(message.from_user.id, InputFile('Photo/remont.jpg'), caption=remont,
                                 reply_markup=bt_reg)
        case 'Диагностика':
            await bot.send_photo(message.from_user.id, InputFile('Photo/diag.jpg'), caption=diag, reply_markup=bt_reg)
        case 'Апгрейд ПК':
            await bot.send_message(message.from_user.id, text='Ну тут нужно чекать в ДНС цены.',
                                   reply_markup=bt_uprgade)
        case 'Удаление вирусов':
            await bot.send_photo(message.from_user.id, InputFile("Photo/virus.jpg"), caption=virus)
        case 'Если просто не включается компьютер?':
            await bot.send_message(message.from_user.id,
                                   text='А может ну его... Компы эти сложные, а?\n и кстати, не пишите сюда больше')
            await bot.send_message(message.from_user.id, text='Бан по причине тупоголовый')
        case 'Сборка':
            await bot.send_message(message.from_user.id,
                                   text='Привозите свои комплектующие. Мы поможем вам собрать ПК и дадим советы')

