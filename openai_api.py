import logging
from openai import AsyncOpenAI
from openai._exceptions import OpenAIError, RateLimitError
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Async OpenAI client
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def get_funny_reply(user_message: str) -> str:
    if not user_message.strip():
        return "❗ Matn bo‘sh bo‘lishi mumkin emas."

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Sen IT Creative jamoasi tomonidan yaratilgan quvnoq Telegram botsan. "
                        "Javoblaring do‘stona, quvnoq va hazilomuz bo‘lsin."
                    ),
                },
                {"role": "user", "content": user_message.strip()},
            ],
            temperature=0.8,
        )
        return response.choices[0].message.content.strip()

    except RateLimitError:
        return "⛔ Juda ko‘p so‘rov yuborildi. Iltimos, keyinroq urinib ko‘ring."

    except OpenAIError as e:
        logging.error(f"[OPENAI XATO] {e}")
        return f"⚠️ OpenAI bilan bog‘lanishda xatolik: {str(e)}"

    except Exception as e:
        logging.exception("❌ Nomaʼlum xatolik yuz berdi.")
        return "⚠️ Ichki xatolik yuz berdi. Iltimos, keyinroq urinib ko‘ring."
