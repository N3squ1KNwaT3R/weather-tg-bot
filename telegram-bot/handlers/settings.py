from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from loguru import logger

from utils.api_client import api_client

settings_router = Router()


class SettingsStates(StatesGroup):
    waiting_for_city = State()


@settings_router.message(Command("setcity"))
async def set_city_command(message: types.Message, state: FSMContext):
    await message.answer("🏙️ Введи название своего города (по-польски):")
    await state.set_state(SettingsStates.waiting_for_city)


@settings_router.message(SettingsStates.waiting_for_city)
async def process_set_city(message: types.Message, state: FSMContext):
    city = message.text.strip()
    user_id = message.from_user.id

    try:
        results = await api_client.search_city(city)

        logger.info(f"Search results: {results}")

        if not results or len(results) == 0:
            await message.answer("❌ Город не найден.")
            return


        city_data = results[0]
        city_id = city_data.get('id')
        city_name = city_data.get('title')

        logger.info(f"Setting city: id={city_id}, name={city_name}")
        await api_client.set_default_city(user_id, city_name, city_id)

        await message.answer(
            f"✅ Дефолтный город установлен: {city_name}\n\n"
            f"Теперь можешь узнать погоду командой /weather"
        )

        await state.clear()
        logger.info(f"User {user_id} set default city: {city_name}")

    except Exception as e:
        await message.answer("❌ Ошибка при установке города. Попробуй еще раз.")
        logger.error(f"Set city error for user {user_id}: {e}")