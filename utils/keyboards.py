from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📜 Ma'lumotlar"),
            KeyboardButton(text="✍️ Ariza yuborish")
        ]
    ],
    resize_keyboard=True
)

admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📩 Arizalarni ko‘rish"),
            KeyboardButton(text="📩 Arizalar arxiv")
        ],
        [
            KeyboardButton(text="📝 Ma'lumotlarni tahrirlash")
        ]
    ],
    resize_keyboard=True
)


def request_reply_keyboard(request_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📝 Javob yozish", callback_data=f"reply_{request_id}")]
        ]
    )


def archived_request_keyboard(request_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ O'chirish", callback_data=f"delete_{request_id}")]
        ]
    )


info_management_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Qo‘shish", callback_data="admin_info_add"),
            InlineKeyboardButton(text="✏️ Tahrirlash", callback_data="admin_info_edit")
        ],
        [
            InlineKeyboardButton(text="❌ O‘chirish", callback_data="admin_info_delete"),
            InlineKeyboardButton(text="📜 Ko‘rish", callback_data="admin_info_view")
        ]
    ]
)
