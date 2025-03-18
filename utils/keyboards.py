from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from translations import LANG


def get_main_menu(lang: str):
    main = LANG[lang]["main_menu"]
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=main["info"])],
            [KeyboardButton(text=main["request"])],
            [KeyboardButton(text=main["change_language"])]
        ],
        resize_keyboard=True
    )


def get_admin_menu(lang: str):
    admin = LANG[lang]["admin_menu"]
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=admin["view_requests"]), KeyboardButton(text=admin["archived_requests"])],
            [KeyboardButton(text=admin["edit_info"]), KeyboardButton(text=admin["change_language"])]
        ],
        resize_keyboard=True
    )


def request_reply_keyboard(request_id, lang: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📝", callback_data=f"reply_{request_id}")]
        ]
    )


def archived_request_keyboard(request_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌", callback_data=f"delete_{request_id}")]
        ]
    )


def get_info_management_menu(lang: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="➕", callback_data="admin_info_add"),
                InlineKeyboardButton(text="✏️", callback_data="admin_info_edit")
            ],
            [
                InlineKeyboardButton(text="❌", callback_data="admin_info_delete"),
                InlineKeyboardButton(text="📜", callback_data="admin_info_view")
            ]
        ]
    )


def get_language_selection_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🇺🇿 Uzbek", callback_data="set_lang_uz"),
             InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang_ru")]
        ]
    )


def get_phone_number_keyboard(lang: str):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=LANG[lang]["enter_phone"], request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
