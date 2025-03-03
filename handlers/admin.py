from aiogram import Router, types, F
from aiogram.filters import Command
from config import ADMIN_IDS
from database import get_requests, update_request_status, update_info
from utils.keyboards import admin_menu

# Create a router for admin handlers
router = Router()


# Admin panel access
@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id in ADMIN_IDS:
        await message.answer("Admin panelga xush kelibsiz!", reply_markup=admin_menu)
    else:
        await message.answer("Sizga ruxsat berilmagan.")


# View student requests
@router.message(F.text == "📩 Arizalarni ko‘rish")
async def view_requests(message: types.Message):
    if message.from_user.id in ADMIN_IDS:
        requests = get_requests()
        if not requests:
            await message.answer("Hozircha arizalar yo‘q.")
        else:
            for req in requests:
                await message.answer(
                    f"📌 ID: {req[0]}\n"
                    f"👤 Ism: {req[1]}\n"
                    f"📚 Guruh: {req[2]}\n"
                    f"📝 Ariza: {req[3]}\n"
                    f"📍 Holat: {req[4]}"
                )
    else:
        await message.answer("Sizga ruxsat berilmagan.")


# Edit information section
@router.message(Command("edit_info"))
async def edit_info(message: types.Message):
    if message.from_user.id in ADMIN_IDS:
        parts = message.text.split(" ", 2)
        if len(parts) < 3:
            await message.answer("Foydalanish: /edit_info <bo‘lim> <yangi ma'lumot>")
            return

        section, content = parts[1], parts[2]
        update_info(section, content)
        await message.answer(f"📜 {section.capitalize()} bo‘limi yangilandi!")
    else:
        await message.answer("Sizga ruxsat berilmagan.")
