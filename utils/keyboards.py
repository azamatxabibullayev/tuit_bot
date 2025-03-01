from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(KeyboardButton("📜 Ma'lumotlar"), KeyboardButton("✍️ Ariza yuborish"))

info_menu = InlineKeyboardMarkup(row_width=1)
info_menu.add(
    InlineKeyboardButton("🏛 Rektorat", callback_data="info_rektorat"),
    InlineKeyboardButton("📖 Dekanat", callback_data="info_dekanat"),
    InlineKeyboardButton("📂 Bo‘limlar", callback_data="info_bolimlar"),
)

admin_menu = ReplyKeyboardMarkup(resize_keyboard=True)
admin_menu.add(KeyboardButton("📩 Arizalarni ko‘rish"), KeyboardButton("📝 Ma'lumotlarni tahrirlash"))
