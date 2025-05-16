from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.filters import Command, CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import sqlite3

from app.keyboard import edit_kb, in_db, not_in_db, show_pass, hide_pass, cancel_kb


router = Router()

class Registration(StatesGroup):
    waiting_for_login = State()
    waiting_for_password = State()

class EditInfo(StatesGroup):
    editing_login = State()
    text_old_password = State()
    editing_password = State()
    edit_profile_pic = State()


@router.message(CommandStart())
async def start_message(message: Message):
    con = sqlite3.connect('data.db')
    cr = con.cursor()

    cr.execute("""CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY,
    login TEXT NOT NULL,
    password TEXT NOT NULL,
    id_profile_pic TEXT
    )""")
    cr.execute(f"""SELECT * FROM Users WHERE id = {message.from_user.id}""")
    if cr.fetchone():
        await message.answer('Вы уже есть в БД ✅. Можете удалить аккаунт или изменить данные', reply_markup=in_db)
    else:
        await message.answer('Приветствую! Здесь вы можете зарегистрироваться в супер технологичную и безопасную базу данных', reply_markup=not_in_db)

    con.commit()
    con.close()


@router.message(F.text == 'Зарегистрироваться в БД')
async def start_reg(message: Message, state: FSMContext):
    con = sqlite3.connect('data.db')
    cr = con.cursor()
    cr.execute(f"SELECT * FROM Users WHERE id = '{message.from_user.id}'")
    if cr.fetchone():
        await message.answer('Вы уже зарегистрированы ✅')
    else:
        await message.answer('Отлично! Пожалуйста введите ваш логин: ', reply_markup=cancel_kb)
        await state.set_state(Registration.waiting_for_login)


@router.message(Registration.waiting_for_login)
async def get_name(message: Message, state: FSMContext):
    if message.text == 'Отмена ❌':
        await message.answer('Регистрация отменена ✅')
        await state.clear()
        return

    con = sqlite3.connect('data.db')
    cr = con.cursor()
    cr.execute(f"SELECT * FROM Users WHERE login = '{message.text}'")
    if not cr.fetchone():
        await state.update_data(login=message.text)
        await state.set_state(Registration.waiting_for_password)
        await message.answer('Отлично! Теперь введите пароль: ', reply_markup=cancel_kb)
    else:
        await message.answer('Такой пользователь уже существует. Пожалуйста, введите другой логин: ', reply_markup=cancel_kb)

    con.commit()
    con.close()


@router.message(Registration.waiting_for_password)
async def get_password(message: Message, state: FSMContext):
    if message.text == 'Отмена ❌':
        await message.answer('Регистрация отменена ✅')
        await state.clear()
        return

    await state.update_data(password=message.text)
    data = await state.get_data()
    con = sqlite3.connect('data.db')
    cr = con.cursor()

    cr.execute(f"INSERT INTO Users VALUES ({message.from_user.id}, '{data['login']}', '{data['password']}', 'None')")

    con.commit()
    con.close()

    await message.answer(f'Отлично! Регистрация завершена ✅\n\nВаш логин {data['login']}\nВаш пароль: {data['password']}', reply_markup=in_db)
    await state.clear()


@router.message(F.text == 'Мой профиль')
async def check_profile(message: Message):
    con = sqlite3.connect('data.db')
    cr = con.cursor()

    cr.execute(f"SELECT * FROM Users WHERE id = {message.from_user.id}")
    data = cr.fetchone()
    if data:
        if data[3] != 'None':
            await message.answer_photo(photo=data[3], caption='Фото профиля')
        await message.answer(f'Ваш логин: {data[1]}\nВаш пароль: {'*' * len(data[2])}', reply_markup=show_pass)
    else:
        await message.answer('Вы ещё не зарегистрированы в БД', reply_markup=not_in_db)

    con.commit()
    cr.close()


@router.callback_query(F.data == 'showpass')
async def show_password(callback: CallbackQuery):
    con = sqlite3.connect('data.db')
    cr = con.cursor()

    cr.execute(f"SELECT * FROM Users WHERE id = {callback.from_user.id}")
    data = cr.fetchone()
    if data:
        await callback.answer('Показать пароль')
        await callback.message.edit_text(f'Ваш логин: {data[1]}\nВаш пароль: {data[2]}', reply_markup=hide_pass)
    else:
        await callback.answer('Вы не зарегистрированы')
        await callback.message.answer('Вы ещё не зарегистрированы в БД', reply_markup=not_in_db)

    con.commit()
    cr.close()


@router.callback_query(F.data == 'hidepass')
async def hide_password(callback: CallbackQuery):
    con = sqlite3.connect('data.db')
    cr = con.cursor()

    cr.execute(f"SELECT * FROM Users WHERE id = {callback.from_user.id}")
    data = cr.fetchone()
    if data:
        await callback.answer('Скрыть пароль')
        await callback.message.edit_text(f'Ваш логин: {data[1]}\nВаш пароль: {'*' * len(data[2])}', reply_markup=show_pass)
    else:
        await callback.answer('Вы не зарегистрированы')
        await callback.message.answer('Вы ещё не зарегистрированы в БД', reply_markup=not_in_db)

    con.commit()
    cr.close()


@router.message(F.text == 'Удалить аккаунт')
async def del_acc(message: Message):
    con = sqlite3.connect('data.db')
    cr = con.cursor()

    cr.execute(f'SELECT * FROM Users WHERE id = {message.from_user.id}')

    if cr.fetchone():
        cr.execute(f'DELETE FROM Users WHERE id = {message.from_user.id}')
        con.commit()
        con.close()
        await message.answer('Аккаунт удалён ✅', reply_markup=not_in_db)
    else:
        await message.answer('Вы ещё не зарегистрированы в БД', reply_markup=not_in_db)


@router.message(F.text == 'Изменить данные')
async def edit_acc(message: Message):
    con = sqlite3.connect('data.db')
    cr = con.cursor()

    cr.execute(f'SELECT * FROM Users WHERE id = {message.from_user.id}')
    if not cr.fetchone():
        await message.answer('Вы ещё не зарегистрированы в БД', reply_markup=not_in_db)
    else:
        await message.answer('Отлично! Выберите, что хотите изменить:', reply_markup=edit_kb)

    con.commit()
    con.close()


@router.callback_query(F.data == 'editlogin')
async def change_login(callback: CallbackQuery, state: FSMContext):
    con = sqlite3.connect('data.db')
    cr = con.cursor()

    cr.execute(f"SELECT login FROM Users WHERE id = {callback.from_user.id}")
    if cr.fetchone():
        await callback.answer('Вы выбрали изменить логин ✅')
        await callback.message.answer('Введите новый логин:', reply_markup=cancel_kb)
        await state.set_state(EditInfo.editing_login)
    else:
        await callback.message.answer('Вы ещё не зарегистрированы в БД', reply_markup=not_in_db)

    con.commit()
    con.close()


@router.callback_query(F.data == 'editpassword')
async def change_password(callback: CallbackQuery, state: FSMContext):
    con = sqlite3.connect('data.db')
    cr = con.cursor()

    cr.execute(f"SELECT login FROM Users WHERE id = {callback.from_user.id}")
    if cr.fetchone():
        await callback.answer('Вы выбрали изменить пароль ✅')
        await callback.message.answer('Сначала введите старый пароль:', reply_markup=cancel_kb)
        await state.set_state(EditInfo.text_old_password)
    else:
        await callback.message.answer('Вы ещё не зарегистрированы в БД', reply_markup=not_in_db)

    con.commit()
    con.close()


@router.callback_query(F.data == 'canceledit')
async def cancel_edit(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Вы выбрали отмену')
    await callback.message.answer('Хорошо ✅')
    await callback.message.delete()
    await state.clear()


@router.message(EditInfo.editing_login)
async def edit_login(message: Message, state: FSMContext):
    if message.text == 'Отмена ❌':
        await message.answer('Хорошо ✅')
        await state.clear()
        return

    con = sqlite3.connect('data.db')
    cr = con.cursor()

    cr.execute(f"SELECT login FROM Users WHERE id = {message.from_user.id}")
    data = cr.fetchone()
    if not data:
        await message.answer('Вы ещё не зарегистрированы в БД', reply_markup=not_in_db)
    elif data[0] == message.text:
        await message.answer('Вы ввели свой же логин, пожалуйста, введите другой:', reply_markup=cancel_kb)
    else:
        cr.execute(f"SELECT * FROM Users WHERE login = '{message.text}'")
        if cr.fetchone():
            await message.answer('Такой пользователь уже существует. Пожалуйста, введите другой логин:', reply_markup=in_db)
        else:
            cr.execute(f"UPDATE Users SET login = '{message.text}' WHERE id = {int(message.from_user.id)}")
            await state.clear()
            await message.answer(f'Логин успешно изменён ✅\nНовый логин: {message.text}', reply_markup=in_db)

    con.commit()
    con.close()


@router.message(EditInfo.text_old_password)
async def wait_for_old_password(message: Message, state: FSMContext):
    if message.text == 'Отмена ❌':
        await message.answer('Хорошо ✅')
        await state.clear()
        return

    con = sqlite3.connect('data.db')
    cr = con.cursor()

    cr.execute(f"SELECT password FROM Users WHERE id = {message.from_user.id}")
    data = cr.fetchone()
    if data and data[0] == message.text:
        await message.answer('Отлично! Вы ввели верный пароль\nВведите новый пароль:', reply_markup=cancel_kb)
        await state.set_state(EditInfo.editing_password)
    else:
        await message.answer('Пароль неверный. Пожалуйста, попробуйте снова', reply_markup=cancel_kb)

    con.commit()
    con.close()


@router.message(EditInfo.editing_password)
async def editing_password(message: Message, state: FSMContext):
    if message.text == 'Отмена ❌':
        await message.answer('Хорошо ✅')
        await state.clear()
        return

    con = sqlite3.connect('data.db')
    cr = con.cursor()

    cr.execute(f"SELECT * FROM Users WHERE id = {message.from_user.id}")
    data = cr.fetchone()

    if not data:
        await message.answer('Вы ещё не зарегистрированы в БД', reply_markup=not_in_db)
    else:
        cr.execute(f"UPDATE Users SET password = '{message.text}' WHERE id = {message.from_user.id}")
        await message.answer(f'Пароль успешно изменён ✅\nНовый пароль: {message.text}', reply_markup=in_db)
        await state.clear()

    con.commit()
    con.close()


@router.message(F.text == 'Добавить/изменить аватарку профиля')
async def get_profile_pic(message: Message, state: FSMContext):
    await message.answer('Отправьте фотографию в чат:', reply_markup=cancel_kb)
    await state.set_state(EditInfo.edit_profile_pic)


@router.message(EditInfo.edit_profile_pic)
async def set_profile_pic(message: Message, state: FSMContext):
    if message.text == 'Отмена ❌':
        await message.answer('Хорошо ✅')
        await state.clear()
        return

    if message.content_type == ContentType.PHOTO:
        con = sqlite3.connect('data.db')
        cr = con.cursor()

        cr.execute(f"UPDATE Users SET id_profile_pic = '{message.photo[-1].file_id}' WHERE id = {message.from_user.id}")
        await message.answer('Фото профиля установлено ✅', reply_markup=in_db)
        await state.clear()

        con.commit()
        con.close()
    else:
        await message.answer('Пожалуйста, отправьте не сжатую фотографию для вашего профиля в чат')


@router.message(Command('all'), F.from_user.id == 1999317423)
async def list_of_users(message: Message):
    con = sqlite3.connect('data.db')
    cr = con.cursor()

    cr.execute('SELECT * FROM Users')
    users = ''

    for i, info in enumerate(cr.fetchall(), start=1):
        user_id, login, password = info[:3]
        users += f'{i}. id = {user_id}, {login} - {password}\n'

    await message.answer(users)

    con.commit()
    con.close()


@router.message()
async def cant_understand(message: Message):
    await start_message(message)