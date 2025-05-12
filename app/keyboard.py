from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def create_markup(buttons):
    markup = ReplyKeyboardBuilder()
    for btn in buttons:
        markup.add(KeyboardButton(text=btn))
    return markup.adjust(2).as_markup(resize_keyboard=True)