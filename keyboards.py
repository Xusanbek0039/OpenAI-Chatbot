from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🚀 Kursga yozilish", 
                url="https://itclms.uz/signup"  # <-- bu yerga havolangizni yozing
            )
        ],
        [
            InlineKeyboardButton(
                text="Admin bilan bog'lanish", 
                callback_data="admin"
            )
        ],
        [
            InlineKeyboardButton(
                text="Chatni boshlash", 
                callback_data="start_fun"
            )
        ]
    ])
