import openai
from config import OPENAI_API_KEY
import logging

openai.api_key = OPENAI_API_KEY

async def get_funny_reply(user_message: str) -> str:
    if not user_message.strip():
        return "❗ Matn bo‘sh bo‘lishi mumkin emas."

    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4o",  # Istasangiz: "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "Sen IT Creative jamoasi tomonidan yaratilgan quvnoq telegram botsan. Javoblaring do‘stona va quvnoq bo‘lsin."},
                {"role": "user", "content": user_message.strip()}
            ],
            temperature=0.8,  # 1.1 dan balandroq xavfliroq: haddan ortiq kreativ
        )
        return response.choices[0].message.content.strip()

    except openai.error.OpenAIError as e:
        logging.error(f"[OPENAI ERROR] {e}")
        return f"⚠️ OpenAI bilan bog‘lanishda xatolik: {str(e)}"

    except Exception as e:
        logging.exception("❌ Nomaʼlum xatolik yuz berdi.")
        return "⚠️ Ichki xatolik yuz berdi. Iltimos, keyinroq urinib ko‘ring."





