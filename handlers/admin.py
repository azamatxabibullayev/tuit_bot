from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
from config import ADMIN_IDS
from database import (
    get_requests, get_archived_requests, update_request_status,
    get_request, delete_request,
    add_info_item, get_all_info_items, get_info_item, update_info_item, delete_info_item
)
from utils.keyboards import (
    admin_menu, request_reply_keyboard, archived_request_keyboard,
    info_management_menu
)

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
    except Exception:
        await message.answer("Xatolik yuz berdi, iltimos qaytadan urinib ko‘ring.")
        return

    req = get_request(request_id)
    if req:
        user_id = req[1]
        try:
            await message.bot.send_message(user_id, f"Sizning arizangizga javob:\n\n{reply_text}")
        except Exception:
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
        except Exception:
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
    waiting_for_title = State()
    waiting_for_link = State()
    waiting_for_parent_id = State()


@router.callback_query(F.data == "admin_info_add")
async def info_add(callback: CallbackQuery, state: FSMContext):
    if is_admin(callback.from_user.id):
        await callback.message.answer("Yangi bo'lim nomini kiriting:")
        await state.set_state(InfoAdd.waiting_for_title)
        await callback.answer()
    else:
        await callback.message.answer("Sizga ruxsat berilmagan.")
        await callback.answer()


@router.message(InfoAdd.waiting_for_title)
async def info_add_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await message.answer(
        "Agar bu bo'limga link (URL) biriktirmoqchi bo'lsangiz kiriting. Agar link bo'lmasa 'yoq' deb yozing:")
    await state.set_state(InfoAdd.waiting_for_link)


@router.message(InfoAdd.waiting_for_link)
async def info_add_link(message: types.Message, state: FSMContext):
    link = message.text.strip()
    if link.lower() == "yoq":
        link = None
    await state.update_data(link=link)
    await message.answer("Agar bu bo'limning ota bo'limi bo'lsa, ota bo'lim ID sini kiriting. Bo'lmasa '0' deb yozing:")
    await state.set_state(InfoAdd.waiting_for_parent_id)


@router.message(InfoAdd.waiting_for_parent_id)
async def info_add_parent_id(message: types.Message, state: FSMContext):
    parent_id_str = message.text.strip()
    try:
        parent_id = int(parent_id_str)
    except ValueError:
        await message.answer("Noto'g'ri ID kiritildi, qayta kiriting yoki '0' deb yozing:")
        return

    if parent_id == 0:
        parent_id = None

    data = await state.get_data()
    title = data["title"]
    link = data["link"]

    add_info_item(title, link, parent_id)
    await message.answer(f"✅ Yangi bo'lim qo'shildi: {title}")
    await state.clear()


class InfoEdit(StatesGroup):
    waiting_for_item_id = State()
    waiting_for_new_title = State()
    waiting_for_new_link = State()


@router.callback_query(F.data == "admin_info_edit")
async def info_edit(callback: CallbackQuery, state: FSMContext):
    if is_admin(callback.from_user.id):
        all_items = get_all_info_items()
        if not all_items:
            await callback.message.answer("Hech qanday bo'lim mavjud emas.")
            await callback.answer()
            return
        text = "Tahrirlash uchun ID ni tanlang:\n"
        for item in all_items:
            text += f"ID: {item[0]} | Title: {item[2]} | Link: {item[3]}\n"
        await callback.message.answer(text)
        await callback.message.answer("Tahrir qilmoqchi bo'lgan bo'limning ID sini kiriting:")
        await state.set_state(InfoEdit.waiting_for_item_id)
        await callback.answer()
    else:
        await callback.message.answer("Sizga ruxsat berilmagan.")
        await callback.answer()


@router.message(InfoEdit.waiting_for_item_id)
async def info_edit_item_id(message: types.Message, state: FSMContext):
    try:
        item_id = int(message.text.strip())
    except ValueError:
        await message.answer("Noto'g'ri ID. Qayta kiriting:")
        return
    item = get_info_item(item_id)
    if not item:
        await message.answer("Bunday ID mavjud emas. Qayta kiriting:")
        return
    await state.update_data(item_id=item_id)
    await message.answer("Yangi nomni kiriting (o'zgartirmoqchi bo'lmasangiz 'yoq' deb yozing):")
    await state.set_state(InfoEdit.waiting_for_new_title)


@router.message(InfoEdit.waiting_for_new_title)
async def info_edit_new_title(message: types.Message, state: FSMContext):
    new_title = message.text.strip()
    if new_title.lower() == "yoq":
        new_title = None
    await state.update_data(new_title=new_title)
    await message.answer("Yangi linkni kiriting (o'zgartirmoqchi bo'lmasangiz 'yoq' deb yozing):")
    await state.set_state(InfoEdit.waiting_for_new_link)


@router.message(InfoEdit.waiting_for_new_link)
async def info_edit_new_link(message: types.Message, state: FSMContext):
    new_link = message.text.strip()
    if new_link.lower() == "yoq":
        new_link = None
    data = await state.get_data()
    item_id = data["item_id"]
    new_title = data["new_title"]
    update_info_item(item_id, new_title, new_link)
    await message.answer("✅ Ma'lumot muvaffaqiyatli tahrirlandi.")
    await state.clear()


class InfoDelete(StatesGroup):
    waiting_for_item_id = State()


@router.callback_query(F.data == "admin_info_delete")
async def info_delete(callback: CallbackQuery, state: FSMContext):
    if is_admin(callback.from_user.id):
        all_items = get_all_info_items()
        if not all_items:
            await callback.message.answer("Hech qanday bo'lim mavjud emas.")
            await callback.answer()
            return
        text = "O'chirish uchun ID ni tanlang:\n"
        for item in all_items:
            text += f"ID: {item[0]} | Title: {item[2]} | Link: {item[3]}\n"
        await callback.message.answer(text)
        await callback.message.answer("O'chirmoqchi bo'lgan bo'limning ID sini kiriting:")
        await state.set_state(InfoDelete.waiting_for_item_id)
        await callback.answer()
    else:
        await callback.message.answer("Sizga ruxsat berilmagan.")
        await callback.answer()


@router.message(InfoDelete.waiting_for_item_id)
async def info_delete_item_id(message: types.Message, state: FSMContext):
    try:
        item_id = int(message.text.strip())
    except ValueError:
        await message.answer("Noto'g'ri ID. Qayta kiriting:")
        return
    item = get_info_item(item_id)
    if not item:
        await message.answer("Bunday ID mavjud emas. Qayta kiriting:")
        return
    delete_info_item(item_id)
    await message.answer("✅ Bo'lim o'chirildi.")
    await state.clear()


@router.callback_query(F.data == "admin_info_view")
async def info_view_admin(callback: CallbackQuery):
    if is_admin(callback.from_user.id):
        all_items = get_all_info_items()
        if not all_items:
            await callback.message.answer("Ma'lumotlar mavjud emas.")
        else:
            text = "Hozirgi bo'limlar:\n"
            for item in all_items:
                text += f"ID: {item[0]}, Parent: {item[1]}, Title: {item[2]}, Link: {item[3]}\n"
            await callback.message.answer(text)
        await callback.answer()
    else:
        await callback.message.answer("Sizga ruxsat berilmagan.")
        await callback.answer()
