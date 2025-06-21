from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI
from datetime import datetime

client = AsyncIOMotorClient(MONGO_URI)
db = client["funny_bot"]
users_collection = db["users"]
messages_collection = db["messages"]

async def save_user_message(user, text: str):
    # Foydalanuvchini users kollektsiyasida yangilash yoki qo‘shish
    await users_collection.update_one(
        {"user_id": user.id},
        {
            "$set": {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
            },
            "$setOnInsert": {"user_id": user.id}
        },
        upsert=True
    )

    # Yuborilgan xabarni messages kollektsiyasiga saqlash
    await messages_collection.insert_one({
        "user_id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "message": text,
        "timestamp": datetime.utcnow()  # UTC vaqti bilan
    })
