from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton

# Главное меню
button_menu = InlineKeyboardButton('-|Меню')
button_inc = InlineKeyboardButton('📝|Канал')
button_help = InlineKeyboardButton('🆘|Помощь')

bt_sec = ReplyKeyboardMarkup(resize_keyboard=True).add(button_menu).row(
  button_inc, button_help)