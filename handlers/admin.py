from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
from config import ADMIN_IDS
from database import (get_requests, get_archived_requests, update_request_status,
                      update_info, get_info, delete_info, get_request, get_all_info, delete_request)
from utils.keyboards import admin_menu, request_reply_keyboard, info_management_menu, archived_request_keyboard

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
                    f"✅ Javob: {req[7]}",
                    reply_markup=archived_request_keyboard(req[0])
                )
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


@router.callback_query(F.data.startswith("delete_"))
async def delete_archived_request(callback: CallbackQuery):
    if is_admin(callback.from_user.id):
        request_id = int(callback.data.split("_")[1])
        try:
            delete_request(request_id)
        except Exception as e:
            await callback.message.answer("Xatolik yuz berdi. Iltimos, qaytadan urinib ko‘ring.")
            await callback.answer()
            return
        await callback.message.answer("Ariza muvaffaqiyatli o'chirildi!")
        await callback.answer()
    else:
        await callback.message.answer("Sizga ruxsat berilmagan.")
        await callback.answer()


@router.message(F.text == "📝 Ma'lumotlarni tahrirlash")
async def manage_info(message: types.Message):
    if is_admin(message.from_user.id):
        await message.answer("Ma'lumotlarni boshqarish:", reply_markup=info_management_menu)
    else:
        await message.answer("Sizga ruxsat berilmagan.")


class InfoAdd(StatesGroup):
    waiting_for_section = State()
    waiting_for_content = State()


class InfoDelete(StatesGroup):
    waiting_for_section = State()


@router.callback_query(F.data == "admin_info_add")
async def info_add(callback: CallbackQuery, state: FSMContext):
    if is_admin(callback.from_user.id):
        await callback.message.answer("Qo‘shmoqchi bo‘lgan bo‘lim nomini kiriting:")
        await state.set_state(InfoAdd.waiting_for_section)
        await callback.answer()
    else:
        await callback.message.answer("Sizga ruxsat berilmagan.")
        await callback.answer()


@router.message(InfoAdd.waiting_for_section)
async def info_add_section(message: types.Message, state: FSMContext):
    await state.update_data(section=message.text.strip())
    await message.answer("Ushbu bo‘lim uchun URL manzilini kiriting:")
    await state.set_state(InfoAdd.waiting_for_content)


@router.message(InfoAdd.waiting_for_content)
async def info_add_content(message: types.Message, state: FSMContext):
    data = await state.get_data()
    section = data.get("section")
    content = message.text.strip()
    update_info(section, content)
    await message.answer(f"📜 {section.capitalize()} bo‘limi qo‘shildi yoki tahrirlandi!")
    await state.finish()


@router.callback_query(F.data == "admin_info_edit")
async def info_edit(callback: CallbackQuery, state: FSMContext):
    if is_admin(callback.from_user.id):
        await callback.message.answer("Tahrirlash uchun bo‘lim nomini kiriting:")
        await state.set_state(InfoAdd.waiting_for_section)
        await callback.answer()
    else:
        await callback.message.answer("Sizga ruxsat berilmagan.")
        await callback.answer()


@router.callback_query(F.data == "admin_info_delete")
async def info_delete(callback: CallbackQuery, state: FSMContext):
    if is_admin(callback.from_user.id):
        await callback.message.answer("O‘chirmoqchi bo‘lgan bo‘lim nomini kiriting:")
        await state.set_state(InfoDelete.waiting_for_section)
        await callback.answer()
    else:
        await callback.message.answer("Sizga ruxsat berilmagan.")
        await callback.answer()


@router.message(InfoDelete.waiting_for_section)
async def info_delete_section(message: types.Message, state: FSMContext):
    section = message.text.strip()
    delete_info(section)
    await message.answer(f"📜 {section.capitalize()} bo‘limi o‘chirildi!")
    await state.finish()


@router.callback_query(F.data == "admin_info_view")
async def info_view_admin(callback: CallbackQuery):
    if is_admin(callback.from_user.id):
        all_info = get_all_info()
        if not all_info:
            await callback.message.answer("Ma'lumotlar mavjud emas.")
        else:
            for section, content in all_info:
                await callback.message.answer(f"📜 {section.capitalize()}:\n\n{content}")
        await callback.answer()
    else:
        await callback.message.answer("Sizga ruxsat berilmagan.")
        await callback.answer()
