from aiogram import types, Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from loguru import logger
from datetime import datetime

from utils.api_client import api_client

registration_router = Router()


class RegistrationStates(StatesGroup):
    waiting_for_email = State()
    waiting_for_code = State()


@registration_router.message(CommandStart())
async def start_registration(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.from_user.username

    try:
        user_info = await api_client.get_user_info(user_id)

        if user_info.get("is_verified"):
            city = user_info.get("city", "Не установлен")
            email = user_info.get("email", "Не указан")
            registered_at = user_info.get("created_at", "")

            if registered_at:
                try:
                    reg_date = datetime.fromisoformat(registered_at.replace("Z", "+00:00"))
                    reg_date_str = reg_date.strftime("%d.%m.%Y %H:%M")
                except:
                    reg_date_str = registered_at
            else:
                reg_date_str = "Неизвестно"

            current_time = datetime.now().strftime("%d.%m.%Y %H:%M")

            await message.answer(
                f"👋 С возвращением, {user_name or 'друг'}!\n\n"
                f"📧 Email: {email}\n"
                f"🏙️ Город: {city}\n"
                f"📅 Дата регистрации: {reg_date_str}\n"
                f"🕐 Текущее время: {current_time}\n\n"
                f"Используй /help для списка команд"
            )
            await state.clear()
            return


        else:
            await message.answer(
                "⚠️ Ты начал регистрацию, но не завершил верификацию.\n"
                "Введи свой email снова:"
            )
            await state.set_state(RegistrationStates.waiting_for_email)
            return

    except Exception as e:

        logger.info(f"New user {user_id} starting registration: {e}")

    await message.answer(
        "👋 Привет! Я бот для прогноза погоды.\n\n"
        "Для начала работы нужно зарегистрироваться.\n"
        "Введи свой email:"
    )

    await state.set_state(RegistrationStates.waiting_for_email)
    logger.info(f"User {user_id} ({user_name}) started registration")


@registration_router.message(RegistrationStates.waiting_for_email)
async def process_email(message: types.Message, state: FSMContext):
    email = message.text.strip()
    user_id = message.from_user.id

    if "@" not in email or "." not in email:
        await message.answer("❌ Неверный формат email. Попробуй еще раз:")
        return

    try:
        result = await api_client.register(user_id, email)

        await message.answer(
            f"✅ Код верификации отправлен на {email}\n\n"
            "Введи 6-значный код из письма:"
        )

        await state.update_data(email=email)
        await state.set_state(RegistrationStates.waiting_for_code)

        logger.info(f"Verification code sent to {email} for user {user_id}")

    except Exception as e:
        await message.answer(
            "❌ Ошибка регистрации. Возможно, ты уже зарегистрирован.\n"
            "Попробуй /start заново."
        )
        await state.clear()
        logger.error(f"Registration error for user {user_id}: {e}")


@registration_router.message(RegistrationStates.waiting_for_code)
async def process_code(message: types.Message, state: FSMContext):
    code = message.text.strip()
    user_id = message.from_user.id

    if len(code) != 6 or not code.isdigit():
        await message.answer("❌ Код должен состоять из 6 цифр. Попробуй еще раз:")
        return

    try:
        result = await api_client.verify(user_id, code)

        await message.answer(
            "✅ Верификация успешна!\n\n"
            "Теперь настрой свой город командой /setcity\n"
            "или сразу узнай погоду командой /weather"
        )

        await state.clear()
        logger.info(f"User {user_id} verified successfully")

    except Exception as e:
        await message.answer(
            "❌ Неверный или истекший код.\n"
            "Попробуй еще раз или начни регистрацию заново /start"
        )
        logger.error(f"Verification error for user {user_id}: {e}")
