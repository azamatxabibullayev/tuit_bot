from aiogram import Router, types, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ADMIN_IDS
from database import add_request, get_child_items, get_info_item
from utils import keyboards
from translations import LANG
from language_manager import get_language, set_language

router = Router()


class StudentForm(StatesGroup):
    full_name = State()
    group_number = State()
    phone_number = State()
    request_text = State()
    review = State()


@router.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
    lang = get_language(message.from_user.id)
    if lang is None:
        await message.answer(LANG["uz"]["select_language"], reply_markup=keyboards.get_language_selection_keyboard())
    else:
        if message.from_user.id in ADMIN_IDS:
            await message.answer(LANG[lang]["admin_welcome"], reply_markup=keyboards.get_admin_menu(lang))
        else:
            await message.answer(LANG[lang]["start_message"], reply_markup=keyboards.get_main_menu(lang))


@router.callback_query(F.data.startswith("set_lang_"))
async def set_language_callback(callback: types.CallbackQuery, state: FSMContext):
    lang_code = callback.data.split("_")[2]
    if lang_code not in ["uz", "ru"]:
        lang_code = "uz"
    set_language(callback.from_user.id, lang_code)
    if callback.from_user.id in ADMIN_IDS:
        await callback.message.answer(LANG[lang_code]["admin_welcome"],
                                      reply_markup=keyboards.get_admin_menu(lang_code))
    else:
        await callback.message.answer(LANG[lang_code]["start_message"], reply_markup=keyboards.get_main_menu(lang_code))
    await callback.answer()


@router.message(F.text.in_([LANG["uz"]["main_menu"]["info"], LANG["ru"]["main_menu"]["info"]]))
async def info_menu_handler(message: Message):
    lang = get_language(message.from_user.id) or "uz"
    await show_info_items(message, lang)


async def show_info_items(message_or_callback, lang: str, parent_id=None):
    items = get_child_items(parent_id)
    if not items:
        if parent_id is not None:
            item = get_info_item(parent_id)
            if item and item[4]:
                kb = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text=LANG[lang]["open_link"], url=item[4])]
                    ]
                )
                text = "Bu bo'limda havola mavjud:" if lang == "uz" else "В этом разделе есть ссылка:"
                if isinstance(message_or_callback, Message):
                    await message_or_callback.answer(text, reply_markup=kb)
                else:
                    await message_or_callback.message.answer(text, reply_markup=kb)
            else:
                text = "Bu bo'limda qo'shimcha ma'lumot yo'q." if lang == "uz" else "В этом разделе нет дополнительной информации."
                if isinstance(message_or_callback, Message):
                    await message_or_callback.answer(text)
                else:
                    await message_or_callback.message.answer(text)
        else:
            text = "Hozircha ma'lumotlar mavjud emas." if lang == "uz" else "Данных пока нет."
            if isinstance(message_or_callback, Message):
                await message_or_callback.answer(text)
            else:
                await message_or_callback.message.answer(text)
        return

    inline_btns = []
    for (id_, title_uz, title_ru, link) in items:
        title = title_uz if lang == "uz" else title_ru
        if link:
            inline_btns.append([InlineKeyboardButton(text=title, url=link)])
        else:
            inline_btns.append([InlineKeyboardButton(text=title, callback_data=f"info_{id_}")])
    kb = InlineKeyboardMarkup(inline_keyboard=inline_btns)
    text = "Kerakli bo‘limni tanlang:" if lang == "uz" else "Выберите раздел:"
    if isinstance(message_or_callback, Message):
        await message_or_callback.answer(text, reply_markup=kb)
    else:
        await message_or_callback.message.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("info_"))
async def info_callback_handler(callback: types.CallbackQuery):
    lang = get_language(callback.from_user.id) or "uz"
    item_id = int(callback.data.split("_")[1])
    await show_info_items(callback, lang, parent_id=item_id)
    await callback.answer()


@router.message(F.text.in_([LANG["uz"]["main_menu"]["request"], LANG["ru"]["main_menu"]["request"]]))
async def ariza_command(message: Message, state: FSMContext):
    lang = get_language(message.from_user.id) or "uz"
    if message.from_user.id in ADMIN_IDS:
        await message.answer(
            "Siz admin ekansiz. Ariza yuborish mumkin emas." if lang == "uz" else "Вы администратор. Отправка заявки невозможна.")
        return
    await message.answer(LANG[lang]["enter_full_name"])
    await state.set_state(StudentForm.full_name)


@router.message(StudentForm.full_name)
async def full_name_step(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    lang = get_language(message.from_user.id) or "uz"
    await message.answer(LANG[lang]["enter_group"])
    await state.set_state(StudentForm.group_number)


@router.message(StudentForm.group_number)
async def group_number_step(message: Message, state: FSMContext):
    await state.update_data(group_number=message.text)
    lang = get_language(message.from_user.id) or "uz"
    await message.answer(LANG[lang]["enter_phone"], reply_markup=keyboards.get_phone_number_keyboard(lang))
    await state.set_state(StudentForm.phone_number)


@router.message(StudentForm.phone_number)
async def phone_number_step(message: Message, state: FSMContext):
    lang = get_language(message.from_user.id) or "uz"
    phone = message.contact.phone_number if message.contact else message.text.strip()
    await state.update_data(phone_number=phone)
    await message.answer(LANG[lang]["enter_request_text"])
    await state.set_state(StudentForm.request_text)


@router.message(StudentForm.request_text)
async def request_text_step(message: Message, state: FSMContext):
    lang = get_language(message.from_user.id) or "uz"
    await state.update_data(request_text=message.text)
    data = await state.get_data()
    review_text = LANG[lang]["review_request"].format(
        full_name=data["full_name"],
        group_number=data["group_number"],
        phone_number=data["phone_number"],
        request_text=data["request_text"]
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LANG[lang]["submit"], callback_data="submit_request"),
         InlineKeyboardButton(text=LANG[lang]["cancel"], callback_data="cancel_request")]
    ])
    await message.answer(review_text, reply_markup=keyboard)
    await state.set_state(StudentForm.review)


@router.callback_query(F.data == "submit_request")
async def submit_request(callback: types.CallbackQuery, state: FSMContext):
    lang = get_language(callback.from_user.id) or "uz"
    data = await state.get_data()
    add_request(
        callback.from_user.id,
        data["full_name"],
        data["group_number"],
        data["phone_number"],
        data["request_text"]
    )
    await callback.message.answer(LANG[lang]["request_submitted"], reply_markup=keyboards.get_main_menu(lang))
    await state.clear()
    from config import ADMIN_IDS
    notification = LANG[lang]["new_request_notification"].format(
        full_name=data["full_name"],
        group_number=data["group_number"],
        request_text=data["request_text"]
    )
    for admin_id in ADMIN_IDS:
        try:
            admin_lang = get_language(admin_id) or "uz"
            await callback.message.bot.send_message(admin_id, notification,
                                                    reply_markup=keyboards.get_admin_menu(admin_lang))
        except Exception:
            continue
    await callback.answer()


@router.callback_query(F.data == "cancel_request")
async def cancel_request(callback: types.CallbackQuery, state: FSMContext):
    lang = get_language(callback.from_user.id) or "uz"
    await callback.message.answer(LANG[lang]["request_cancelled"], reply_markup=keyboards.get_main_menu(lang))
    await state.clear()
    await callback.answer()


@router.message(F.text.in_([LANG["uz"]["main_menu"]["change_language"], LANG["ru"]["main_menu"]["change_language"]]))
async def change_language(message: Message):
    lang = get_language(message.from_user.id) or "uz"
    await message.answer(LANG[lang]["select_language"], reply_markup=keyboards.get_language_selection_keyboard())
