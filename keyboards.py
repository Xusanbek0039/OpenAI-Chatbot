from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import ADMIN_ID

def get_start_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="🚀 Kursga yozilish")],
        [
            KeyboardButton(text="📞 Admin bilan bog‘lanish"),
            KeyboardButton(text="📊 Limitingizni ko‘rish")
        ],
    ]

    if user_id == ADMIN_ID:
        admin_buttons = [
            KeyboardButton(text="📊 Statistika"),
            KeyboardButton(text="✅ Limit berish"),
            KeyboardButton(text="❌ Cheksiz limitlar"),
        ]

        # Har 2 tadan qatorga joylash
        admin_rows = [admin_buttons[i:i+2] for i in range(0, len(admin_buttons), 2)]
        buttons += admin_rows

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )
