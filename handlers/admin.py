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
from utils import keyboards
from translations import LANG
from language_manager import get_language

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.message(Command("admin"))
async def admin_start(message: types.Message):
    lang = get_language(message.from_user.id) or "uz"
    if is_admin(message.from_user.id):
        await message.answer(LANG[lang]["admin_welcome"], reply_markup=keyboards.get_admin_menu(lang))
    else:
        await message.answer(LANG[lang]["no_permission"])


@router.message(F.text.in_([LANG["uz"]["admin_menu"]["view_requests"], LANG["ru"]["admin_menu"]["view_requests"]]))
async def view_requests(message: types.Message):
    lang = get_language(message.from_user.id) or "uz"
    if is_admin(message.from_user.id):
        requests = get_requests()
        if not requests:
            await message.answer("Hozircha arizalar yo‘q." if lang == "uz" else "Заявок пока нет.")
        else:
            for req in requests:
                await message.answer(
                    f"📌 ID: {req[0]}\n"
                    f"👤 Ism: {req[2]}\n"
                    f"📚 Guruh: {req[3]}\n"
                    f"📝 Ariza: {req[4]}\n"
                    f"📍 Holat: {req[5]}",
                    reply_markup=keyboards.request_reply_keyboard(req[0], lang)
                )
    else:
        await message.answer(LANG[lang]["no_permission"])


@router.message(
    F.text.in_([LANG["uz"]["admin_menu"]["archived_requests"], LANG["ru"]["admin_menu"]["archived_requests"]]))
async def view_archived_requests(message: types.Message):
    lang = get_language(message.from_user.id) or "uz"
    if is_admin(message.from_user.id):
        archived = get_archived_requests()
        if not archived:
            await message.answer("Arxivda hech qanday ariza mavjud emas." if lang == "uz" else "Архив заявок пуст.")
        else:
            for req in archived:
                await message.answer(
                    f"📌 ID: {req[0]}\n"
                    f"👤 Ism: {req[2]}\n"
                    f"📚 Guruh: {req[3]}\n"
                    f"📝 Ariza: {req[5]}\n"
                    f"✅ Javob: {req[7]}",
                    reply_markup=keyboards.archived_request_keyboard(req[0])
                )
    else:
        await message.answer(LANG[lang]["no_permission"])


class AdminReply(StatesGroup):
    waiting_for_reply = State()


@router.callback_query(F.data.startswith("reply_"))
async def reply_request(callback: CallbackQuery, state: FSMContext):
    lang = get_language(callback.from_user.id) or "uz"
    if is_admin(callback.from_user.id):
        request_id = int(callback.data.split("_")[1])
        await state.update_data(request_id=request_id)
        await callback.message.answer(LANG[lang]["admin_reply_prompt"].format(request_id=request_id))
        await state.set_state(AdminReply.waiting_for_reply)
        await callback.answer()
    else:
        await callback.message.answer(LANG[lang]["no_permission"])
        await callback.answer()


@router.message(AdminReply.waiting_for_reply)
async def process_admin_reply(message: types.Message, state: FSMContext):
    lang = get_language(message.from_user.id) or "uz"
    data = await state.get_data()
    request_id = data.get("request_id")
    reply_text = message.text.strip()

    if not request_id:
        await message.answer(LANG[lang]["error"])
        return

    try:
        update_request_status(request_id, "answered", admin_reply=reply_text)
    except Exception:
        await message.answer(LANG[lang]["error"])
        return

    req = get_request(request_id)
    if req:
        user_id = req[1]
        try:
            await message.bot.send_message(user_id,
                                           f"Sizning arizangizga javob:\n\n{reply_text}" if lang == "uz" else f"Ваш ответ на заявку:\n\n{reply_text}")
        except Exception:
            await message.answer(
                "Foydalanuvchiga javob yuborishda xatolik yuz berdi. Iltimos, foydalanuvchi botni ishga tushirganga ishonch hosil qiling." if lang == "uz" else "Ошибка при отправке ответа пользователю. Убедитесь, что пользователь запустил бота.")
    else:
        await message.answer("Ariza topilmadi." if lang == "uz" else "Заявка не найдена.")

    await message.answer(LANG[lang]["request_answered"])
    await state.clear()


@router.callback_query(F.data.startswith("delete_"))
async def delete_archived_request(callback: CallbackQuery):
    lang = get_language(callback.from_user.id) or "uz"
    if is_admin(callback.from_user.id):
        request_id = int(callback.data.split("_")[1])
        try:
            delete_request(request_id)
        except Exception:
            await callback.message.answer(LANG[lang]["error"])
            await callback.answer()
            return
        await callback.message.answer("Ariza muvaffaqiyatli o'chirildi!" if lang == "uz" else "Заявка успешно удалена!")
        await callback.answer()
    else:
        await callback.message.answer(LANG[lang]["no_permission"])
        await callback.answer()


@router.message(F.text.in_([LANG["uz"]["admin_menu"]["edit_info"], LANG["ru"]["admin_menu"]["edit_info"]]))
async def manage_info(message: types.Message):
    lang = get_language(message.from_user.id) or "uz"
    if is_admin(message.from_user.id):
        await message.answer("Ma'lumotlarni boshqarish:" if lang == "uz" else "Управление информацией:",
                             reply_markup=keyboards.get_info_management_menu(lang))
    else:
        await message.answer(LANG[lang]["no_permission"])


class InfoAdd(StatesGroup):
    waiting_for_title = State()
    waiting_for_link = State()
    waiting_for_parent_id = State()


@router.callback_query(F.data == "admin_info_add")
async def info_add(callback: CallbackQuery, state: FSMContext):
    lang = get_language(callback.from_user.id) or "uz"
    if is_admin(callback.from_user.id):
        await callback.message.answer(
            "Yangi bo'lim nomini kiriting:" if lang == "uz" else "Введите название нового раздела:")
        await state.set_state(InfoAdd.waiting_for_title)
        await callback.answer()
    else:
        await callback.message.answer(LANG[lang]["no_permission"])
        await callback.answer()


@router.message(InfoAdd.waiting_for_title)
async def info_add_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    lang = get_language(message.from_user.id) or "uz"
    await message.answer(
        "Agar bu bo'limga link (URL) biriktirmoqchi bo'lsangiz kiriting. Agar link bo'lmasa 'yoq' deb yozing:" if lang == "uz" else "Если хотите добавить ссылку (URL) к этому разделу, введите её. Если нет, напишите 'нет':")
    await state.set_state(InfoAdd.waiting_for_link)


@router.message(InfoAdd.waiting_for_link)
async def info_add_link(message: types.Message, state: FSMContext):
    lang = get_language(message.from_user.id) or "uz"
    link = message.text.strip()
    if link.lower() in ["yoq", "нет"]:
        link = None
    await state.update_data(link=link)
    await message.answer(
        "Agar bu bo'limning ota bo'limi bo'lsa, ota bo'lim ID sini kiriting. Bo'lmasa '0' deb yozing:" if lang == "uz" else "Если этот раздел имеет родительский раздел, введите его ID. Если нет, введите '0':")
    await state.set_state(InfoAdd.waiting_for_parent_id)


@router.message(InfoAdd.waiting_for_parent_id)
async def info_add_parent_id(message: types.Message, state: FSMContext):
    lang = get_language(message.from_user.id) or "uz"
    parent_id_str = message.text.strip()
    try:
        parent_id = int(parent_id_str)
    except ValueError:
        await message.answer(
            "Noto'g'ri ID kiritildi, qayta kiriting yoki '0' deb yozing:" if lang == "uz" else "Неверный ID, попробуйте снова или введите '0':")
        return

    if parent_id == 0:
        parent_id = None

    data = await state.get_data()
    title = data["title"]
    link = data["link"]

    add_info_item(title, link, parent_id)
    await message.answer(LANG[lang]["info_added"].format(title=title))
    await state.clear()


class InfoEdit(StatesGroup):
    waiting_for_item_id = State()
    waiting_for_new_title = State()
    waiting_for_new_link = State()


@router.callback_query(F.data == "admin_info_edit")
async def info_edit(callback: CallbackQuery, state: FSMContext):
    lang = get_language(callback.from_user.id) or "uz"
    if is_admin(callback.from_user.id):
        all_items = get_all_info_items()
        if not all_items:
            await callback.message.answer(
                "Hech qanday bo'lim mavjud emas." if lang == "uz" else "Нет доступных разделов.")
            await callback.answer()
            return
        text = "Tahrirlash uchun ID ni tanlang:\n" if lang == "uz" else "Выберите ID для редактирования:\n"
        for item in all_items:
            text += f"ID: {item[0]} | Title: {item[2]} | Link: {item[3]}\n"
        await callback.message.answer(text)
        await callback.message.answer(
            "Tahrir qilmoqchi bo'lgan bo'limning ID sini kiriting:" if lang == "uz" else "Введите ID раздела, который хотите отредактировать:")
        await state.set_state(InfoEdit.waiting_for_item_id)
        await callback.answer()
    else:
        await callback.message.answer(LANG[lang]["no_permission"])
        await callback.answer()


@router.message(InfoEdit.waiting_for_item_id)
async def info_edit_item_id(message: types.Message, state: FSMContext):
    lang = get_language(message.from_user.id) or "uz"
    try:
        item_id = int(message.text.strip())
    except ValueError:
        await message.answer("Noto'g'ri ID. Qayta kiriting:" if lang == "uz" else "Неверный ID, попробуйте снова:")
        return
    item = get_info_item(item_id)
    if not item:
        await message.answer(
            "Bunday ID mavjud emas. Qayta kiriting:" if lang == "uz" else "Такого ID не существует, попробуйте снова:")
        return
    await state.update_data(item_id=item_id)
    await message.answer(
        "Yangi nomni kiriting (o'zgartirmoqchi bo'lmasangiz 'yoq' deb yozing):" if lang == "uz" else "Введите новое название (если не хотите менять, введите 'нет'):")
    await state.set_state(InfoEdit.waiting_for_new_title)


@router.message(InfoEdit.waiting_for_new_title)
async def info_edit_new_title(message: types.Message, state: FSMContext):
    new_title = message.text.strip()
    lang = get_language(message.from_user.id) or "uz"
    if new_title.lower() in ["yoq", "нет"]:
        new_title = None
    await state.update_data(new_title=new_title)
    await message.answer(
        "Yangi linkni kiriting (o'zgartirmoqchi bo'lmasangiz 'yoq' deb yozing):" if lang == "uz" else "Введите новую ссылку (если не хотите менять, введите 'нет'):")
    await state.set_state(InfoEdit.waiting_for_new_link)


@router.message(InfoEdit.waiting_for_new_link)
async def info_edit_new_link(message: types.Message, state: FSMContext):
    new_link = message.text.strip()
    lang = get_language(message.from_user.id) or "uz"
    if new_link.lower() in ["yoq", "нет"]:
        new_link = None
    data = await state.get_data()
    item_id = data["item_id"]
    new_title = data["new_title"]
    update_info_item(item_id, new_title, new_link)
    await message.answer(LANG[lang]["info_updated"])
    await state.clear()


class InfoDelete(StatesGroup):
    waiting_for_item_id = State()


@router.callback_query(F.data == "admin_info_delete")
async def info_delete(callback: CallbackQuery, state: FSMContext):
    lang = get_language(callback.from_user.id) or "uz"
    if is_admin(callback.from_user.id):
        all_items = get_all_info_items()
        if not all_items:
            await callback.message.answer(
                "Hech qanday bo'lim mavjud emas." if lang == "uz" else "Нет доступных разделов.")
            await callback.answer()
            return
        text = "O'chirish uchun ID ni tanlang:\n" if lang == "uz" else "Выберите ID для удаления:\n"
        for item in all_items:
            text += f"ID: {item[0]} | Title: {item[2]} | Link: {item[3]}\n"
        await callback.message.answer(text)
        await callback.message.answer(
            "O'chirmoqchi bo'lgan bo'limning ID sini kiriting:" if lang == "uz" else "Введите ID раздела, который хотите удалить:")
        await state.set_state(InfoDelete.waiting_for_item_id)
        await callback.answer()
    else:
        await callback.message.answer(LANG[lang]["no_permission"])
        await callback.answer()


@router.message(InfoDelete.waiting_for_item_id)
async def info_delete_item_id(message: types.Message, state: FSMContext):
    lang = get_language(message.from_user.id) or "uz"
    try:
        item_id = int(message.text.strip())
    except ValueError:
        await message.answer("Noto'g'ri ID. Qayta kiriting:" if lang == "uz" else "Неверный ID, попробуйте снова:")
        return
    item = get_info_item(item_id)
    if not item:
        await message.answer(
            "Bunday ID mavjud emas. Qayta kiriting:" if lang == "uz" else "Такого ID не существует, попробуйте снова:")
        return
    delete_info_item(item_id)
    await message.answer(LANG[lang]["info_deleted"])
    await state.clear()


@router.callback_query(F.data == "admin_info_view")
async def info_view_admin(callback: CallbackQuery):
    lang = get_language(callback.from_user.id) or "uz"
    if is_admin(callback.from_user.id):
        all_items = get_all_info_items()
        if not all_items:
            await callback.message.answer("Ma'lumotlar mavjud emas." if lang == "uz" else "Нет данных.")
        else:
            text = "Hozirgi bo'limlar:\n" if lang == "uz" else "Текущие разделы:\n"
            for item in all_items:
                text += f"ID: {item[0]}, Parent: {item[1]}, Title: {item[2]}, Link: {item[3]}\n"
            await callback.message.answer(text)
        await callback.answer()
    else:
        await callback.message.answer(LANG[lang]["no_permission"])
        await callback.answer()
