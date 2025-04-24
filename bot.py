import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import BotCommand
from aiogram.filters import Command
from config import TOKEN
from handlers.student import router as student_router
from handlers.admin import router as admin_router
from database import create_tables
from language_manager import get_language

logging.basicConfig(level=logging.INFO)

create_tables()

bot = Bot(token=TOKEN)
dp = Dispatcher()

dp.include_router(student_router)
dp.include_router(admin_router)


@dp.message(Command("help"))
async def help_handler(message: types.Message):
    lang = get_language(message.from_user.id) or "uz"
    help_text = (
        "Bu bot orqali siz o'z arizangizni fakultetga yozishingiz mumkin"
        if lang == "uz"
        else "С помощью этого бота вы можете отправить заявку в факультет"
    )
    await message.answer(help_text)


async def set_commands():
    commands = [
        BotCommand(command="start", description="Botni boshlash / Запустить бота"),
        BotCommand(command="help",
                   description="Yordam / Справка")
    ]
    await bot.set_my_commands(commands)


async def main():
    await set_commands()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
