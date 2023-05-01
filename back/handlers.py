import re
import time

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InputFile, WebAppInfo, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.exceptions import CantInitiateConversation

from back.config import CHANNEL_ID
from back.form_kons import konsult
from back.form_reg import register
from back.form_upgrade import upgrade

# from form_reg import register
from keyboards import bt_sec, kb1, bt_kat
from main import bot, dp
from texts import place, comp, remont


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.answer(
        f'''Привет, {message.from_user.username}!\nЯ бот, с помощью которого можно узнать статус своего заказа''',
        reply_markup=bt_sec)
    time.sleep(1)
    await main_menu(message)


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

@dp.callback_query_handler(text_contains='', state='*')
async def all_message(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state()
    await state.finish()
    code = callback.data
    match code:
        case 'katalog':
            await bot.send_photo(callback.from_user.id, InputFile("Photo/remont.png"), caption=remont,
                                 reply_markup=bt_kat)
        case 'place':
            await bot.send_photo(callback.from_user.id, InputFile("Photo/map.PNG"), caption=place, reply_markup=bt_sec)
            await bot.send_location(callback.from_user.id, 55.544813, 37.516697, 'Сервиго', 'Москва')
            time.sleep(1)
            await main_menu(callback)
        case 'company':
            await bot.send_photo(callback.from_user.id, InputFile("Photo/gorshok.jpg"), caption=comp,
                                 reply_markup=bt_sec)
            time.sleep(1)
            await main_menu(callback)


@dp.message_handler(text_contains='', state='*')
async def kat_info(message: types.Message, state: FSMContext):
    await state.set_state()
    await state.finish()
    code = message.text
    bt_reg = InlineKeyboardMarkup()
    bt_reg.add(InlineKeyboardButton(text='Оставить заявку на ремонт', callback_data='register'))
    bt_uprgade = InlineKeyboardMarkup()
    bt_uprgade.add(InlineKeyboardButton(text='Осавьте заявку на апгрейд', callback_data='upgrade'))
    match code:
        case 'Ремонт':
            await bot.send_message(message.from_user.id, text='''Ну это категория ремонта\nтут описание ремнтных 
работ и прочая хуйня\nПо кнопке ниже Вы можете оставить заявку на ремонт''', reply_markup=bt_reg)

        case 'Диагностика':
            await bot.send_message(message.from_user.id, text='Все проверим и скажем что не так', reply_markup=bt_reg)
        case 'Апгрейд ПК':
            await bot.send_message(message.from_user.id, text='Ну тут нужно чекать в ДНС цены.', reply_markup=bt_uprgade)
        case 'Удаление вирусов':
            await bot.send_message(message.from_user.id, text='нахуй не нужны вам эти вирусы поганые!\nМы это, антисептик ваш.')
        case 'Если просто не включается компьютер?':
            await bot.send_message(message.from_user.id, text='А может ну его... Компы эти сложные, а?\n и кстати, не пишите сюда больше')
            await bot.send_message(message.from_user.id, text='Бан по причине тупоголовый')
        case 'Сборка':
            await bot.send_message(message.from_user.id, text='Оставьте заявку на сборку пк. Если нужны дополнительные комплектующие, сообщите.')



@dp.callback_query_handler(text='register')
async def my_callback_handler(callback_query: types.CallbackQuery):
    try:
        print("Button clicked!")
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, "Button clicked!")
    except Exception as e:
        print(f"Error: {e}")


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

    bt_info=InlineKeyboardMarkup()
    bt_info.add(InlineKeyboardButton(text='Кнопка для вопросов', callback_data='info'))

    # Парсим id из сообщения
    head = message.reply_to_message.text.split('\n')[0].split()[0]
    if head == 'Обращение':
        uid = message.reply_to_message.text.split('\n')[2].split()[1]
        feedback = message.reply_to_message.text.split('\n')[5]
        text = f'"{feedback}"'
        try:
            await bot.send_message(uid, f'''{text}
⚠Ответ от администратора: 👇🏻\n{message.text}
В случае возникновения вопросов или уточнений, напишите по кнопке ниже''',reply_markup=bt_info)
        except CantInitiateConversation:
            await bot.reply("Ошибка\n")
    elif head == 'Заявка':
        uid = message.reply_to_message.text.split('\n')[2].split()[1]
        feedback = message.reply_to_message.text.split('\n')[0].split()[3].rstrip(':')
        text = f'"{feedback}"'
        try:
            await bot.send_message(uid, f'''Ремонт {text}
⚠Ответ от администратора: 👇🏻\n{message.text}
В случае возникновения вопросов или уточнений, напишите по кнопке ниже''',reply_markup=bt_info)
        except CantInitiateConversation:
            await bot.reply("Ошибка\n")
    elif head == 'Модернизация':
        uid = message.reply_to_message.text.split('\n')[2].split()[1]
        try:
            await bot.send_message(uid, f'''Ваша заявка принята.
В случае возникновения вопросов или уточнений, напишите по кнопке ниже''',reply_markup=bt_info)
        except CantInitiateConversation:
            await bot.reply("Ошибка\n")
