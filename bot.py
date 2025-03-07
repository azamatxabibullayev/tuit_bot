import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from config import TOKEN
from handlers.student import router as student_router
from handlers.admin import router as admin_router
from database import create_tables

logging.basicConfig(level=logging.INFO)

create_tables()

bot = Bot(token=TOKEN)
dp = Dispatcher()

dp.include_router(student_router)
dp.include_router(admin_router)


async def set_commands():
    commands = [
        BotCommand(command="start", description="Botni boshlash")
    ]
    await bot.set_my_commands(commands)


async def main():
    await set_commands()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
