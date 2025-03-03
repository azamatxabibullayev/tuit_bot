from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📜 Ma'lumotlar"), KeyboardButton(text="✍️ Ariza yuborish")]
    ],
    resize_keyboard=True
)

info_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🏛 Rektorat", callback_data="info_rektorat")],
        [InlineKeyboardButton(text="📖 Dekanat", callback_data="info_dekanat")],
        [InlineKeyboardButton(text="📂 Bo‘limlar", callback_data="info_bolimlar")]
    ]
)

admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📩 Arizalarni ko‘rish"), KeyboardButton(text="📩 Arizalar arxiv")],
        [KeyboardButton(text="📝 Ma'lumotlarni tahrirlash")]
    ],
    resize_keyboard=True
)


def request_reply_keyboard(request_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📝 Javob yozish", callback_data=f"reply_{request_id}")]
        ]
    )
