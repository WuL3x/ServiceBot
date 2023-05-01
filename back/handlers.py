import re
import time

from aiogram import types
from aiogram.types import InputFile, WebAppInfo
from aiogram.utils.exceptions import CantInitiateConversation

from back.config import CHANNEL_ID
from back.form_kons import konsult
from form_reg import register
from keyboards import bt_sec, kb1
from main import bot, dp
from texts import place, comp


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.answer(
        f'''Привет, {message.from_user.username}!\nЯ бот, с помощью которого можно узнать статус своего заказа''',
        reply_markup=bt_sec)
    await main_menu(message)


@dp.message_handler(text=['Меню'])
async def main_menu(callback: types.callback_query):
    await bot.send_message(callback.from_user.id, reply_markup=kb1, text='Выберите пункт меню 👇🏻')


@dp.callback_query_handler(text=['place'])
async def handle_place(callback: types.CallbackQuery):
    await bot.send_photo(callback.from_user.id, InputFile("Photo/map.PNG"), caption=place, reply_markup=bt_sec)
    await bot.send_location(callback.from_user.id, 55.544813, 37.516697, 'Сервиго', 'Москва')
    time.sleep(1)
    await main_menu(callback)



@dp.callback_query_handler(text=['company'])
async def company(callback: types.CallbackQuery):
    await bot.send_photo(callback.from_user.id, InputFile("Photo/gorshok.jpg"), caption=comp, reply_markup=bt_sec)
    time.sleep(1)
    await main_menu(callback)

konsult()
register()


@dp.message_handler(chat_id=CHANNEL_ID)
async def admin_reply(message: types.Message):
    # me = await bot.get_me()
    # if not message.reply_to_message:
    #     return
    # if message.reply_to_message.from_user.id != me.id:
    #     return
    # if not message.text:
    #     await bot.send_message(message.chat.id, "Я обрабатываю только текст")
    #     return
    # if message.reply_to_message.text.split('\n')[0] not in keyboards.vturmu:
    #     return
    # if not message.reply_to_message.text.__contains__(", "):
    #     return

    # Парсим id из сообщения
    head = message.reply_to_message.text.split('\n')[0].split()[0]
    if head == 'Обращение':
        uid = message.reply_to_message.text.split('\n')[2].split()[1]
        feedback = message.reply_to_message.text.split('\n')[5]
        text = f'"{feedback}"'
        try:
            await bot.send_message(uid, f'''{text}
⚠Ответ от администратора: 👇🏻\n''' + message.text)
        except CantInitiateConversation:
            await bot.reply("Ошибка\n")
    elif head == 'Заявка':
        uid = message.reply_to_message.text.split('\n')[2].split()[1]
        feedback = message.reply_to_message.text.split('\n')[0].split()[3].rstrip(':')
        text = f'"{feedback}"'
        try:
            await bot.send_message(uid,f'''Ремонт {text}
⚠Ответ от администратора: 👇🏻\n''' + message.text)
        except CantInitiateConversation:
            await bot.reply("Ошибка\n")



