from aiogram import Router, types, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ADMIN_IDS
from database import get_info, add_request
from utils.keyboards import main_menu, info_menu, admin_menu

router = Router()


class StudentForm(StatesGroup):
    full_name = State()
    group_number = State()
    phone_number = State()
    request_text = State()


@router.message(Command("start"))
async def start_command(message: Message):
    if message.from_user.id in ADMIN_IDS:
        await message.answer("Admin panelga xush kelibsiz!", reply_markup=admin_menu)
    else:
        await message.answer("TUIT Telegram botiga xush kelibsiz!", reply_markup=main_menu)


@router.message(F.text == "📜 Ma'lumotlar")
async def info_menu_handler(message: Message):
    await message.answer("Kerakli bo‘limni tanlang:", reply_markup=info_menu)


@router.callback_query(F.data.startswith("info_"))
async def send_info(callback_query: CallbackQuery):
    section = callback_query.data.replace("info_", "")
    content = get_info(section)
    await callback_query.message.answer(f"📜 {section.capitalize()} bo‘limi:\n\n{content}")


@router.message(F.text == "✍️ Ariza yuborish")
async def ariza_command(message: Message, state: FSMContext):
    if message.from_user.id in ADMIN_IDS:
        await message.answer("Siz admin ekansiz. Ariza yuborish mumkin emas.")
        return
    await message.answer("✍️ Iltimos, to‘liq ismingizni kiriting:")
    await state.set_state(StudentForm.full_name)


@router.message(StudentForm.full_name)
async def full_name_step(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer("📌 Guruh raqamingizni kiriting:")
    await state.set_state(StudentForm.group_number)


@router.message(StudentForm.group_number)
async def group_number_step(message: Message, state: FSMContext):
    await state.update_data(group_number=message.text)
    await message.answer("📞 Telefon raqamingizni kiriting:")
    await state.set_state(StudentForm.phone_number)


@router.message(StudentForm.phone_number)
async def phone_number_step(message: Message, state: FSMContext):
    await state.update_data(phone_number=message.text)
    await message.answer("✍️ Ariza matnini yozing:")
    await state.set_state(StudentForm.request_text)


@router.message(StudentForm.request_text)
async def request_text_step(message: Message, state: FSMContext):
    data = await state.get_data()
    add_request(message.from_user.id, data["full_name"], data["group_number"], data["phone_number"], message.text)
    await message.answer("✅ Arizangiz yuborildi!", reply_markup=main_menu)
    await state.clear()
