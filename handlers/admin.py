from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
from config import ADMIN_IDS
from database import (get_requests, get_archived_requests, update_request_status,
                      update_info, get_info, delete_info, get_request)
from utils.keyboards import admin_menu, request_reply_keyboard

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.message(Command("admin"))
async def admin_start(message: types.Message):
    if is_admin(message.from_user.id):
        await message.answer("Admin panelga xush kelibsiz!", reply_markup=admin_menu)
    else:
        await message.answer("Sizga ruxsat berilmagan.")


@router.message(F.text == "📩 Arizalarni ko‘rish")
async def view_requests(message: types.Message):
    if is_admin(message.from_user.id):
        requests = get_requests()
        if not requests:
            await message.answer("Hozircha arizalar yo‘q.")
        else:
            for req in requests:
                await message.answer(
                    f"📌 ID: {req[0]}\n"
                    f"👤 Ism: {req[2]}\n"
                    f"📚 Guruh: {req[3]}\n"
                    f"📝 Ariza: {req[4]}\n"
                    f"📍 Holat: {req[5]}",
                    reply_markup=request_reply_keyboard(req[0])
                )
    else:
        await message.answer("Sizga ruxsat berilmagan.")


@router.message(F.text == "📩 Arizalar arxiv")
async def view_archived_requests(message: types.Message):
    if is_admin(message.from_user.id):
        archived = get_archived_requests()
        if not archived:
            await message.answer("Arxivda hech qanday ariza mavjud emas.")
        else:
            for req in archived:
                await message.answer(
                    f"📌 ID: {req[0]}\n"
                    f"👤 Ism: {req[2]}\n"
                    f"📚 Guruh: {req[3]}\n"
                    f"📝 Ariza: {req[5]}\n"
                    f"✅ Javob: {req[7]}"
                )
    else:
        await message.answer("Sizga ruxsat berilmagan.")


@router.message(Command("edit_info"))
async def edit_info(message: types.Message):
    if is_admin(message.from_user.id):
        parts = message.text.split(" ", 2)
        if len(parts) < 3:
            await message.answer("Foydalanish: /edit_info <bo‘lim> <yangi ma'lumot>")
            return
        section, content = parts[1], parts[2]
        update_info(section, content)
        await message.answer(f"📜 {section.capitalize()} bo‘limi yangilandi!")
    else:
        await message.answer("Sizga ruxsat berilmagan.")


@router.message(Command("delete_info"))
async def delete_info_command(message: types.Message):
    if is_admin(message.from_user.id):
        parts = message.text.split(" ", 1)
        if len(parts) < 2:
            await message.answer("Foydalanish: /delete_info <bo‘lim>")
            return
        section = parts[1]
        delete_info(section)
        await message.answer(f"📜 {section.capitalize()} bo‘limi o‘chirildi!")
    else:
        await message.answer("Sizga ruxsat berilmagan.")


class AdminReply(StatesGroup):
    waiting_for_reply = State()


@router.callback_query(F.data.startswith("reply_"))
async def reply_request(callback: CallbackQuery, state: FSMContext):
    if is_admin(callback.from_user.id):
        request_id = int(callback.data.split("_")[1])
        await state.update_data(request_id=request_id)
        await callback.message.answer(f"📝 Ariza ID {request_id} uchun javob yozing:")
        await state.set_state(AdminReply.waiting_for_reply)
        await callback.answer()
    else:
        await callback.message.answer("Sizga ruxsat berilmagan.")
        await callback.answer()


@router.message(AdminReply.waiting_for_reply)
async def process_admin_reply(message: types.Message, state: FSMContext):
    data = await state.get_data()
    request_id = data.get("request_id")
    reply_text = message.text.strip()

    if not request_id:
        await message.answer("Xatolik: Ariza ID topilmadi.")
        return

    try:
        update_request_status(request_id, "answered", admin_reply=reply_text)
    except Exception as e:
        await message.answer("Xatolik yuz berdi, iltimos qaytadan urinib ko‘ring.")
        return

    req = get_request(request_id)
    if req:
        user_id = req[1]
        try:
            await message.bot.send_message(user_id, f"Sizning arizangizga javob:\n\n{reply_text}")
        except Exception as e:
            await message.answer(
                "Foydalanuvchiga javob yuborishda xatolik yuz berdi. Iltimos, foydalanuvchi botni ishga tushirganga ishonch hosil qiling.")
    else:
        await message.answer("Ariza topilmadi.")

    await message.answer("✅ Ariza javobi yuborildi va arxivga qo‘shildi.")
    await state.finish()
