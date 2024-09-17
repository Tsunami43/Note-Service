from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from provider import provider_user
from provider.models import AccessTokenResponse


# Создаем отдельные стейты для входа
class LoginStates(StatesGroup):
    waiting_for_login = State()
    waiting_for_password = State()


# Инициализируем роутер для входа
router = Router()


# Обработчик команды /login (начало входа)
@router.message(Command("login"))
async def handler_login(message: Message, state: FSMContext, user: AccessTokenResponse):
    if not user:
        await message.answer("Введите логин для входа:")
        await state.set_state(LoginStates.waiting_for_login)
    else:
        await message.answer("Вы уже авторизованны")


# Обработчик ввода логина при входе
@router.message(StateFilter(LoginStates.waiting_for_login))
async def handle_login_login(message: Message, state: FSMContext):
    await state.update_data(login=message.text)
    await message.answer("Введите пароль:")
    await state.set_state(LoginStates.waiting_for_password)


# Обработчик ввода пароля при входе
@router.message(StateFilter(LoginStates.waiting_for_password))
async def handle_login_password(message: Message, state: FSMContext):
    user_data = await state.get_data()
    login = user_data.get("login")
    password = message.text
    user = await provider_user.update_telegram_id(login, password, message.from_user.id)
    if not user:
        await message.answer(f"Ошибка входа")
    else:
        await message.answer("Вы успешно авторизовались!")
    await state.clear()
