from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InputFile, WebAppInfo
from aiogram.utils import executor
from aiogram.utils.exceptions import CantInitiateConversation, MessageCantBeDeleted, MessageToDeleteNotFound

from forms import register
from main import bot, dp
from keyboards import bt_sec

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.answer(f'''Привет, {message.from_user.first_name}!\nЯ бот, с помощью которого можно узнать статус своего заказа''', reply_markup=bt_sec)


@dp.message_handler(text=['Меню'])
async def main_menu(message: types.Message):
    kb1 = types.InlineKeyboardMarkup()
    kb1.insert(types.InlineKeyboardButton(text="Оставить заявку", callback_data="register"))
    kb1.add(types.InlineKeyboardButton(text="Статус заказа", web_app=WebAppInfo(url='https://wul3x.github.io/ServerBot-site')))
    await bot.send_message(message.from_user.id, reply_markup=kb1, text='Выберите пукнкт меню 👇🏻')

register()

