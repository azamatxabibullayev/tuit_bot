from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Student main menu
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📜 Ma'lumotlar"), KeyboardButton(text="✍️ Ariza yuborish")]
    ],
    resize_keyboard=True
)

# Info menu (inline buttons)
info_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🏛 Rektorat", callback_data="info_rektorat")],
        [InlineKeyboardButton(text="📖 Dekanat", callback_data="info_dekanat")],
        [InlineKeyboardButton(text="📂 Bo‘limlar", callback_data="info_bolimlar")]
    ]
)

# Admin menu
admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📩 Arizalarni ko‘rish"), KeyboardButton(text="📝 Ma'lumotlarni tahrirlash")]
    ],
    resize_keyboard=True
)
