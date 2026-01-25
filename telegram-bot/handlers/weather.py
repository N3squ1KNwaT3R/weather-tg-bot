from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from loguru import logger

from utils.api_client import api_client

weather_router = Router()


class WeatherStates(StatesGroup):
    waiting_for_custom_city = State()


CONDITION_EMOJI = {
    100: "☀️",   # Ясно
    200: "🌤️",   # Малооблачно
    300: "☁️",   # Облачно
    400: "🌧️",   # Дождь
    500: "⛈️",   # Гроза
    600: "🌨️",   # Снег
    312: "🌨️",   # Небольшой снег
    412: "🌨️",   # Снег с дождем (мокрый снег)
}


def get_weather_emoji(condition: int, temp: int) -> str:
    """Получить эмодзи погоды с учетом температуры"""

    # Если температура ниже 0 и код дождя - это точно снег
    if temp < 0 and condition in [400, 412]:
        return "🌨️"

    # Иначе берем из маппинга
    return CONDITION_EMOJI.get(condition, "🌤️")

def format_weather(forecast: dict) -> str:
    """Форматирование прогноза погоды"""
    city = forecast.get("city", "Неизвестно")
    temp = forecast.get("temp", 0)
    temp_feels = forecast.get("temp_feels", 0)
    temp_min = forecast.get("temp_min", 0)
    temp_max = forecast.get("temp_max", 0)
    condition = forecast.get("condition", 0)
    description = forecast.get("description", "")

    emoji = get_weather_emoji(condition, temp)  # Используем функцию

    return (
        f"{emoji} Погода в {city}\n"
        f"🌡️ Температура: {temp:+d}°C (ощущается как {temp_feels:+d}°C)\n"
        f"📊 Мин/Макс: {temp_min:+d}°C / {temp_max:+d}°C\n"
        f"📍 {description}"
    )

@weather_router.message(Command("weather"))
async def weather_command(message: types.Message, state: FSMContext):
    """Погода - /weather или /weather Warszawa"""
    user_id = message.from_user.id

    # Парсим аргумент команды
    args = message.text.split(maxsplit=1)

    if len(args) > 1:
        # Есть аргумент - город
        city = args[1].strip()
        await get_weather_for_city(message, user_id, city)
    else:
        # Нет аргумента - дефолтный город
        await get_default_weather(message, user_id)


async def get_default_weather(message: types.Message, user_id: int):
    """Получить погоду для дефолтного города"""
    try:
        forecast = await api_client.get_forecast(user_id)
        await message.answer(format_weather(forecast))
        logger.info(f"User {user_id} checked weather for default city")

    except Exception as e:
        await message.answer(
            "❌ Не удалось получить прогноз.\n"
            "Возможно, ты не установил дефолтный город.\n"
            "Используй /setcity или /weather Warszawa"
        )
        logger.error(f"Weather error for user {user_id}: {e}")


async def get_weather_for_city(message: types.Message, user_id: int, city: str):
    """Получить погоду для конкретного города"""
    try:
        # Поиск города
        results = await api_client.search_city(city)

        if not results or len(results) == 0:
            await message.answer(
                f"❌ Город '{city}' не найден.\n"
                "Попробуй ввести по-польски (например: Warszawa, Kraków)"
            )
            return

        city_data = results[0]
        city_id = city_data.get('id')
        city_name = city_data.get('title')

        # Получаем прогноз
        forecast = await api_client.get_forecast(user_id, city_id, city_name)

        await message.answer(format_weather(forecast))
        logger.info(f"User {user_id} checked weather for {city_name}")

    except Exception as e:
        await message.answer("❌ Ошибка при получении прогноза.")
        logger.error(f"Weather error for user {user_id}, city {city}: {e}")

    @weather_router.message(Command("hourly"))
    async def hourly_command(message: types.Message):
        """Почасовой прогноз - /hourly или /hourly Warszawa"""
        user_id = message.from_user.id

        args = message.text.split(maxsplit=1)

        if len(args) > 1:
            city = args[1].strip()
            await get_hourly_for_city(message, user_id, city)
        else:
            await get_default_hourly(message, user_id)

    async def get_default_hourly(message: types.Message, user_id: int):
        """Почасовой прогноз для дефолтного города"""
        try:
            forecast = await api_client.get_hourly_forecast(user_id)
            await message.answer(format_hourly(forecast))

        except Exception as e:
            await message.answer("❌ Не удалось получить почасовой прогноз.")
            logger.error(f"Hourly error for user {user_id}: {e}")

    async def get_hourly_for_city(message: types.Message, user_id: int, city: str):
        """Почасовой прогноз для конкретного города"""
        try:
            results = await api_client.search_city(city)

            if not results:
                await message.answer(f"❌ Город '{city}' не найден.")
                return

            city_data = results[0]
            city_id = city_data.get('id')
            city_name = city_data.get('title')

            forecast = await api_client.get_hourly_forecast(user_id, city_id, city_name)
            await message.answer(format_hourly(forecast))

        except Exception as e:
            await message.answer("❌ Ошибка при получении прогноза.")
            logger.error(f"Hourly error: {e}")

    def format_hourly(forecast: dict) -> str:
        """Форматирование почасового прогноза"""
        city = forecast.get("city", "Неизвестно")
        hours = forecast.get("hours", [])

        if not hours:
            return "❌ Нет данных о почасовом прогнозе"

        result = f"📅 Почасовой прогноз для {city}\n\n"

        # Берем каждый 3-й час
        for i in range(0, len(hours), 3):
            hour_data = hours[i]
            hour = hour_data.get("hour", 0)
            temp = hour_data.get("temp", 0)
            condition = hour_data.get("condition", 0)
            precip = hour_data.get("precip", 0)

            emoji = get_weather_emoji(condition, temp)  # Используем функцию

            result += f"{hour:02d}:00 {emoji} {temp:+d}°C"  # +d для показа знака

            if precip > 20:
                result += f" 💧{precip}%"

            result += "\n"

        return result# Убираем /weatherin - теперь все через /weather


@weather_router.message(Command("tomorrow"))
async def tomorrow_command(message: types.Message):
    """Прогноз на завтра - /tomorrow или /tomorrow Warszawa"""
    user_id = message.from_user.id

    args = message.text.split(maxsplit=1)

    if len(args) > 1:
        city = args[1].strip()
        await get_tomorrow_for_city(message, user_id, city)
    else:
        await get_default_tomorrow(message, user_id)


async def get_default_tomorrow(message: types.Message, user_id: int):
    """Прогноз на завтра для дефолтного города"""
    try:
        forecast = await api_client.get_tomorrow_forecast(user_id)
        await message.answer(format_tomorrow(forecast))

    except Exception as e:
        await message.answer("❌ Не удалось получить прогноз на завтра.")
        logger.error(f"Tomorrow error for user {user_id}: {e}")


async def get_tomorrow_for_city(message: types.Message, user_id: int, city: str):
    """Прогноз на завтра для конкретного города"""
    try:
        results = await api_client.search_city(city)

        if not results:
            await message.answer(f"❌ Город '{city}' не найден.")
            return

        city_data = results[0]
        city_id = city_data.get('id')
        city_name = city_data.get('title')

        forecast = await api_client.get_tomorrow_forecast(user_id, city_id, city_name)
        await message.answer(format_tomorrow(forecast))

    except Exception as e:
        await message.answer("❌ Ошибка при получении прогноза.")
        logger.error(f"Tomorrow error: {e}")


def format_tomorrow(forecast: dict) -> str:
    """Форматирование прогноза на завтра"""
    city = forecast.get("city", "Неизвестно")
    date = forecast.get("date", "")
    temp_avg = forecast.get("temp_avg", 0)
    temp_min = forecast.get("temp_min", 0)
    temp_max = forecast.get("temp_max", 0)
    condition = forecast.get("condition", 0)
    hours = forecast.get("hours", [])

    emoji = get_weather_emoji(condition, temp_avg)

    # Парсим дату
    try:
        from datetime import datetime
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        date_str = date_obj.strftime("%d.%m.%Y")
    except:
        date_str = date

    result = f"📅 Прогноз на завтра ({date_str})\n"
    result += f"🏙️ {city}\n\n"
    result += f"{emoji} Средняя: {temp_avg:+d}°C\n"
    result += f"📊 Мин/Макс: {temp_min:+d}°C / {temp_max:+d}°C\n\n"

    # Добавляем почасовку (каждые 4 часа)
    if hours:
        result += "⏰ По часам:\n"
        for i in range(0, len(hours), 4):
            hour_data = hours[i]
            hour = hour_data.get("hour", 0)
            temp = hour_data.get("temp", 0)
            h_condition = hour_data.get("condition", 0)
            precip = hour_data.get("precip", 0)

            h_emoji = get_weather_emoji(h_condition, temp)

            result += f"{hour:02d}:00 {h_emoji} {temp:+d}°C"

            if precip > 20:
                result += f" 💧{precip}%"

            result += "\n"

    return result