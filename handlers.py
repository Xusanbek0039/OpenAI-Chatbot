from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery
from openai_api import get_funny_reply
from database import save_user_message
from config import ADMIN_ID
from keyboards import get_start_keyboard
import asyncio
import re
import html

router = Router()

# /start komandasi
@router.message(F.text == "/start")
async def cmd_start(message: Message):
    await message.answer(
        f"Salom {message.from_user.full_name}! 👋\nMen deyarli barcha fanlarga javob beruvchi chatbotman 😄",
        reply_markup=get_start_keyboard()
    )

# Admin bilan bog'lanish
@router.callback_query(F.data == "admin")
async def handle_admin(callback: CallbackQuery):
    await callback.message.answer(
        "Admin bilan bog'lanish uchun ushbu havolani bosing:\n\n"
        "<a href='https://t.me/your_admin_username'>👨‍💻 Adminga yozish</a>",
        parse_mode="HTML"
    )
    await callback.answer()




# "Kursga yozilish" tugmasi bosilganda
# @router.callback_query(F.data == "enroll")
# async def handle_enroll(callback: CallbackQuery):
#     await callback.message.answer("Ajoyib! Siz kursga yozildingiz! 📚")
#     await callback.answer()




# "Hazilni boshlaymizmi?" tugmasi bosilganda
@router.callback_query(F.data == "start_fun")
async def handle_fun(callback: CallbackQuery):
    await callback.message.answer("Savol bering, men kulgili javob qaytaraman! 😂")
    await callback.answer()

# Foydalanuvchi matn yuborganda
@router.message()
async def handle_user_message(message: Message, bot: Bot):
    # Ma'lumotlar bazasiga yozamiz
    await save_user_message(message.from_user, message.text)

    # "typing..." animatsiyasi
    for _ in range(2):
        await bot.send_chat_action(message.chat.id, action="typing")
        await asyncio.sleep(1.2)

    # OpenAI'dan javob olish
    reply = await get_funny_reply(message.text)

    # Javob ichida ```code``` bloklari bo‘lsa — ajratamiz
    code_blocks = re.findall(r"```(\w+)?\n([\s\S]*?)```", reply)

    if code_blocks:
        # Oddiy matnlarni ham ajratish
        text_parts = re.split(r"```[\s\S]*?```", reply)

        for idx, code in enumerate(code_blocks):
            lang, code_content = code
            lang = lang if lang else "text"

            # Koddan oldingi oddiy matn
            if idx < len(text_parts):
                text_part = text_parts[idx].strip()
                if text_part:
                    await message.answer(text_part)

            # Kod blokini HTML escape qilib yuborish
            await message.answer(
                f"<b>{lang} kodi:</b>\n<pre language='{lang}'>{html.escape(code_content)}</pre>",
                parse_mode="HTML"
            )

        # Oxirgi matn (koddan keyin)
        if len(text_parts) > len(code_blocks):
            tail = text_parts[-1].strip()
            if tail:
                await message.answer(tail)

    else:
        # Agar kod bo‘lmasa — oddiy javob yuboriladi
        await message.answer(reply)
