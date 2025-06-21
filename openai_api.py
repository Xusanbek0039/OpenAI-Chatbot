import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

async def get_funny_reply(user_message: str) -> str:
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4o",  # yoki "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "Sen hazilkash va quvnoq Telegram yordamchi botisan."},
                {"role": "user", "content": user_message}
            ],
            temperature=1.1,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Xatolik yuz berdi: {e}"
