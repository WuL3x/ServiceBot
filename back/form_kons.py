import time

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, ParseMode, \
    ReplyKeyboardRemove, InlineKeyboardMarkup
from aiogram.utils import markdown
from aiogram.dispatcher.filters import Text

from back.keyboards import bt_sec, bt_feed, kb1
from config import CHANNEL_ID
from main import bot, dp

button_cancel = InlineKeyboardButton('Отмена', callback_data='cancel')
cancelButton = ReplyKeyboardMarkup(resize_keyboard=True).add(button_cancel)



@dp.message_handler(text=['Меню'])
async def main_menu(message: types.Message):
    await bot.send_message(message.from_user.id, reply_markup=kb1, text='Выберите пункт меню 👇🏻')


def konsult():
    class FormKonsult(StatesGroup):
        type_message = State()
        klient_message = State()

    @dp.message_handler(commands='cancel', state='*')
    @dp.message_handler(Text(equals='Отмена', ignore_case=True), state='*')
    async def cancel(message: types.Message, state: FSMContext):
        current_state = await state.get_state()
        if current_state is None:
            return

        await message.answer(
            '''Отмена отправки⛔''',
            reply_markup=bt_sec)
        time.sleep(1)
        await main_menu(message)
        await state.finish()

    # Обработчик для начала обращения в службу технической поддержки
    @dp.callback_query_handler(lambda c: c.data == 'konsult', state="*")
    async def answer_k(callback_query: CallbackQuery, state: FSMContext):
        await callback_query.answer()
        await callback_query.message.answer("Пожалуйста, опишите свой вопрос/претензию полность",
                                            reply_markup=cancelButton)
        ReplyKeyboardRemove()
        await callback_query.message.answer(
            "Выберите тип обращения:", reply_markup=bt_feed)
        await FormKonsult.type_message.set()

    # Обработчик выбора типа обращения
    @dp.callback_query_handler(lambda c: c.data.startswith('feed:'), state=FormKonsult.type_message)
    async def process_type(callback: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            data = callback.data.split(':')
            type_message = data[1]
            await state.update_data(type_message=type_message)

        await bot.send_message(callback.from_user.id, "Введите ваше сообщение:", reply_markup=cancelButton)
        await FormKonsult.klient_message.set()

    # Обработчик ввода сообщения
    @dp.message_handler(state=FormKonsult.klient_message)
    async def process_klient_message(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['klient_message'] = message.text
            text = "Обращение в службу технической поддержки:\n"
            text += f"Пользователь: @{message.from_user.username}\n"
            text += f"TG_ID: {message.from_user.id}\n"
            text += f"Тип обращения: {data['type_message']}\n"
            text += f"------------\n"
            text += f"{data['klient_message']}"

            kb_chat = InlineKeyboardMarkup()
            kb_chat.add(InlineKeyboardButton(text="Перейти в чат",
                                                 url=f"t.me/{message.from_user.username}"))


            # Отправляем сообщение на заданный вами чат или группу в Telegram
            await bot.send_message(CHANNEL_ID, text, reply_markup=kb_chat)
            if data['type_message'] != 'Отзыв':
                await message.answer(
                    "Ваше обращение было успешно отправлено. Мы свяжемся с вами в ближайшее время.",
                    reply_markup=bt_sec)

            # Отправляем сообщение пользователю о том, что обращение было успешно отправлено
            else:
                await message.answer("Благодарим за ваше неравнодушие к нашему сервису!\n"
                                     "Информация будет передана сотрудникам.", reply_markup=bt_sec)
        time.sleep(1)
        await main_menu(message)
        await state.finish()
