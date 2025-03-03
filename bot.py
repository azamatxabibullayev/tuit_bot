import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from config import TOKEN
from handlers.student  import router as student_router
from handlers.admin import  router as admin_router

# Enable logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Register routers
dp.include_router(student_router)
dp.include_router(admin_router)

# Set bot commands
async def set_commands():
    commands = [
        BotCommand(command="start", description="Botni boshlash"),
        BotCommand(command="admin", description="Admin panel"),
        BotCommand(command="edit_info", description="Ma'lumotni tahrirlash"),
    ]
    await bot.set_my_commands(commands)

# Main function
async def main():
    await set_commands()
    await dp.start_polling(bot)

# Run the bot
if __name__ == "__main__":
    asyncio.run(main())
