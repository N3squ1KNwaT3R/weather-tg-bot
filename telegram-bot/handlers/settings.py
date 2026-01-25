from aiogram import Bot
import asyncio


async def check_token():
    token = "8125363071:AAF54DE3ral6ByAmypH8ziib_2sgiTPqqos"  # вставьте свой токен

    try:
        bot = Bot(token=token)
        # Пробуем получить информацию о боте
        me = await bot.get_me()
        print(f"✅ Токен рабочий! Бот: @{me.username}")
        await bot.session.close()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("Проверьте токен!")


if __name__ == "__main__":
    asyncio.run(check_token())