from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


help_button = InlineKeyboardButton(text='Help', callback_data='show_help')

start_keyboard =InlineKeyboardMarkup(inline_keyboard=[[help_button]])

admin_help_button = InlineKeyboardButton(text='Help for admin', callback_data='admin_help')

admin_keyboard =InlineKeyboardMarkup(inline_keyboard=[[admin_help_button]])