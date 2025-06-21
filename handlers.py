from aiogram import F, Router, Bot
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from openai_api import get_funny_reply
from database import (
    save_user_message, get_statistics, get_user_limit_info,
    get_user_by_id, set_user_unlimited, get_unlimited_users
)
from config import ADMIN_ID
from keyboards import get_start_keyboard
import asyncio
import re
import html
import logging

router = Router()

class LimitStates(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_confirmation = State()

class RemoveLimitStates(StatesGroup):
    waiting_for_id_to_remove = State()
    waiting_for_remove_confirmation = State()

@router.message(F.text == "/start")
async def cmd_start(message: Message):
    user = message.from_user
    logging.info(f"[START] {user.full_name} (@{user.username}, ID: {user.id})")

    welcome_text = (
        f"👋 Assalomu alaykum, {user.full_name}!\n"
        "Men sizga sun'iy intellekt asosida javob beruvchi AI yordamchisiman."
        " Quyidagi funksiyalardan foydalanishingiz mumkin:\n"
        f"🆔 Sizning foydalanuvchi ID raqamingiz: `{user.id}`"
        "📊 Har kuni *20 ta* so‘rov yuborish imkoniyatiga egasiz.\n"
        "🔓 Agar siz *cheksiz so‘rov* huquqiga ega bo‘lmoqchi bo‘lsangiz, "
        f"[admin bilan bog‘laning](https://t.me/husanbek_coder) va ID raqamingizni yuboring.\n"
        "👇 Quyidagi tugmalar orqali foydalanishni boshlang!"
    )

    await message.answer(
        welcome_text,
        reply_markup=get_start_keyboard(user.id),
        parse_mode="Markdown"
    )

@router.message(F.text == "📞 Admin bilan bog‘lanish")
async def handle_admin(message: Message):
    await message.answer("Admin bilan bog'lanish uchun quyidagi havolani bosing:\n👉 https://t.me/husanbek_coder")

@router.message(F.text == "🚀 Kursga yozilish")
async def handle_course(message: Message):
    await message.answer("Kursga yozilish uchun havola: https://itclms.uz/signup")

@router.message(F.text == "😄 Chatni boshlash")
async def handle_fun(message: Message):
    await message.answer("Savolingizni yozing, men javob berishga tayyorman! 😎")

@router.message(F.text == "📊 Statistika")
async def handle_stats(message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔ Ushbu bo‘lim faqat administratorlar uchun!")

    stats = await get_statistics()
    last = stats["last_user"]

    text = f"""
📊 <b>Statistik ma'lumotlar:</b>

👥 Umumiy foydalanuvchilar soni: <b>{stats['total_users']}</b>
📨 Bugungi so‘rovlar soni: <b>{stats['today_messages']}</b>
📅 Oxirgi 7 kunlik so‘rovlar: <b>{stats['week_messages']}</b>
🗓️ Oxirgi 30 kunlik so‘rovlar: <b>{stats['month_messages']}</b>
🆕 Bugun faol bo‘lgan foydalanuvchilar: <b>{stats['today_users']}</b>
    """

    if last:
        text += f"""
\n🦓 Oxirgi foydalanuvchi savoli: <b>{last.get('text')}</b>
👤 Ism: <b>{last.get('full_name')}</b> (@{last.get('username')})
🗓️ Sana: <b>{last.get('date')}</b>
        """
    await message.answer(text, parse_mode="HTML")

@router.message(F.text == "📊 Limitingizni ko‘rish")
async def handle_limit_info(message: Message):
    info = await get_user_limit_info(message.from_user.id)
    text = (
        f"📊 <b>Limit ma'lumotlari:</b>\n\n"
        f"🔓 Cheksiz limit: {'✅ Mavjud' if info['unlimited'] else '❌ Yo‘q'}\n"
        f"📨 Bugungi so‘rovlar: <b>{info['today_count']}</b>\n"
        f"🕐 Qolgan so‘rovlar: <b>{info['remaining']}</b>"
    )
    await message.answer(text, parse_mode="HTML")

@router.message(F.text == "✅ Limit berish")
async def handle_limit_request(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔ Ushbu bo‘lim faqat administratorlar uchun!")
    await message.answer("🆔 Iltimos, foydalanuvchi ID raqamini yuboring:")
    await state.set_state(LimitStates.waiting_for_user_id)

@router.message(LimitStates.waiting_for_user_id)
async def process_user_id(message: Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("❗ Iltimos, to‘g‘ri ID raqamini yuboring.")
    user = await get_user_by_id(int(message.text))
    if not user:
        return await message.answer("🚫 Bunday foydalanuvchi topilmadi.")
    await state.update_data(target_user_id=int(message.text))
    markup = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="✅ Ha"), KeyboardButton(text="❌ Yo‘q")]],
        resize_keyboard=True
    )
    await message.answer(
        f"👤 <b>{user['full_name']}</b> (ID: <code>{user['user_id']}</code>)\n\nCheksiz limit berilsinmi?",
        reply_markup=markup,
        parse_mode="HTML"
    )
    await state.set_state(LimitStates.waiting_for_confirmation)

@router.message(LimitStates.waiting_for_confirmation)
async def confirm_limit(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text == "✅ Ha":
        await set_user_unlimited(data["target_user_id"], True)
        await message.answer("✅ Cheksiz limit berildi.", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer("❌ Amaliyot bekor qilindi.", reply_markup=ReplyKeyboardRemove())
    await state.clear()

@router.message(F.text == "❌ Cheksiz limitlar")
async def show_unlimited_users(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔ Ushbu bo‘lim faqat administratorlar uchun!")
    users = await get_unlimited_users()
    if not users:
        return await message.answer("📭 Cheksiz limitga ega foydalanuvchilar mavjud emas.")
    msg = "<b>♾️ Cheksiz limitga ega foydalanuvchilar:</b>\n"
    for i, u in enumerate(users, start=1):
        msg += f"{i}. {u['full_name']} - <code>{u['user_id']}</code>\n"
    msg += "\nCheksiz limitni bekor qilmoqchi bo‘lgan foydalanuvchi ID raqamini kiriting:"
    await message.answer(msg, parse_mode="HTML")
    await state.set_state(RemoveLimitStates.waiting_for_id_to_remove)

@router.message(RemoveLimitStates.waiting_for_id_to_remove)
async def handle_remove_id(message: Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("❗ Iltimos, faqat raqamli ID yuboring.")
    user = await get_user_by_id(int(message.text))
    if not user:
        return await message.answer("🚫 Foydalanuvchi topilmadi.")
    await state.update_data(user_id=int(message.text))
    markup = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="✅ Ha"), KeyboardButton(text="❌ Yo‘q")]],
        resize_keyboard=True
    )
    await message.answer(
        f"{user['full_name']} ({user['user_id']}) foydalanuvchisidan cheksiz limit olib tashlansinmi?",
        reply_markup=markup
    )
    await state.set_state(RemoveLimitStates.waiting_for_remove_confirmation)

@router.message(RemoveLimitStates.waiting_for_remove_confirmation)
async def confirm_remove_limit(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text == "✅ Ha":
        await set_user_unlimited(data["user_id"], False)
        await message.answer("❌ Cheksiz limit olib tashlandi.", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer("❌ Amaliyot bekor qilindi.", reply_markup=ReplyKeyboardRemove())
    await state.clear()

@router.message()
async def handle_user_message(message: Message, bot: Bot):
    user = message.from_user
    limit_info = await get_user_limit_info(user.id)
    if not limit_info["unlimited"] and limit_info["today_count"] >= 20:
        return await message.answer("⛔ Bugungi 20 ta so‘rov limitiga yetdingiz.")
    await save_user_message(user, message.text)
    for _ in range(2):
        await bot.send_chat_action(message.chat.id, action="typing")
        await asyncio.sleep(1.2)
    reply = await get_funny_reply(message.text)
    code_blocks = re.findall(r"```(\w+)?\n([\s\S]*?)```", reply)
    if code_blocks:
        text_parts = re.split(r"```[\s\S]*?```", reply)
        for i, (lang, content) in enumerate(code_blocks):
            if i < len(text_parts):
                await message.answer(text_parts[i].strip())
            await message.answer(
                f"<b>{lang or 'Kod'}:</b>\n<pre language='{lang}'>{html.escape(content)}</pre>",
                parse_mode="HTML"
            )
        if len(text_parts) > len(code_blocks):
            await message.answer(text_parts[-1].strip())
    else:
        await message.answer(reply)
