from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import peewee
import asyncio
import logging


con = peewee.SqliteDatabase('peewee_db.db')

class Person(peewee.Model):
    us_id = peewee.IntegerField(primary_key=True)
    login = peewee.CharField()
    password = peewee.CharField()

    class Meta:
        database = con

Person.create_table()

bot = Bot(token='7722634745:AAHx-wHNxV7hPv5ayWpAbKDlysCKzutK7Kg')
dp = Dispatcher()


class EditLogin(StatesGroup):
    waiting_for_login = State()

@dp.message(CommandStart())
async def start(message: Message):
    print(message.from_user.id, message.from_user.first_name)
    await message.answer(message.from_user.first_name)
    person = Person.get_or_create(us_id=int(message.from_user.id),
                  login=message.from_user.first_name,
                  password='qwerty123')
    if person[1]:
        await message.answer('Мы зарегистрировали вас без вашего согласия, надеюсь вы не против')
    else:
        await message.answer('Ты уже есть, зачем пишешь старт?')

@dp.message(Command('list'))
async def list_with_users(message: Message):
    data = ''
    for person in Person.select():
        data += f"{str(person.us_id)} {person.login} {person.password}\n"
    data += 'Пусто' if not data else ''
    await message.answer(data)


@dp.message(Command('delete'))
async def delete_user(message: Message):
    person = Person.select().where(Person.us_id == int(message.from_user.id)).get_or_none()
    if person:
        person.delete_instance()
        await message.answer('Ну вроде удалил')
    else:
        await message.answer('иди зарегайся')


async def main():
    await dp.start_polling(bot)


@dp.message(Command('edit'))
async def edit_login(message: Message, state: FSMContext):
    await message.answer('Введите новый логин:')
    await state.set_state(EditLogin.waiting_for_login)


@dp.message(EditLogin.waiting_for_login)
async def get_login(message: Message, state: FSMContext):
    new_login = message.text
    Person.update({Person.login: new_login}).where(Person.us_id == int(message.from_user.id))
    await message.answer('изменил')
    await state.clear()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try: asyncio.run(main())
    except KeyboardInterrupt: print('stop')