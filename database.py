from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI
from datetime import datetime, timedelta

# MongoDB'ga ulanish
client = AsyncIOMotorClient(MONGO_URI)
db = client["openai_bot"]  # MongoDB bazangiz nomi

# ✅ Foydalanuvchi xabarini saqlash
async def save_user_message(user, text):
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)

    # Foydalanuvchini ro‘yxatga olish yoki mavjudligini tekshirish
    await db.users.update_one(
        {"user_id": user.id},
        {
            "$setOnInsert": {
                "user_id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "unlimited": 0,
                "joined_at": now
            }
        },
        upsert=True
    )

    # Agar unlimited maydoni mavjud bo‘lmasa, uni qo‘shish
    await db.users.update_one(
        {"user_id": user.id, "unlimited": {"$exists": False}},
        {"$set": {"unlimited": 0}}
    )

    # Xabarni saqlash
    await db.messages.insert_one({
        "user_id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "text": text,
        "date": now
    })

# ✅ Statistika olish
async def get_statistics():
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    total_users_list = await db.messages.distinct("user_id")
    total_users = len(total_users_list)

    today_messages = await db.messages.count_documents({"date": {"$gte": today_start}})
    week_messages = await db.messages.count_documents({"date": {"$gte": week_ago}})
    month_messages = await db.messages.count_documents({"date": {"$gte": month_ago}})

    today_users_cursor = db.messages.aggregate([
        {"$match": {"date": {"$gte": today_start}}},
        {"$group": {"_id": "$user_id"}}
    ])
    today_users = len([doc async for doc in today_users_cursor])

    last_msg = await db.messages.find().sort("date", -1).limit(1).to_list(length=1)
    last_user = None
    if last_msg:
        doc = last_msg[0]
        last_user = {
            "full_name": doc.get("full_name"),
            "username": doc.get("username"),
            "text": doc.get("text"),
            "date": doc.get("date").strftime("%Y-%m-%d %H:%M:%S")
        }

    return {
        "total_users": total_users,
        "today_messages": today_messages,
        "week_messages": week_messages,
        "month_messages": month_messages,
        "today_users": today_users,
        "last_user": last_user
    }

# ✅ Foydalanuvchining limit holatini olish
async def get_user_limit_info(user_id: int):
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)

    user_doc = await db.users.find_one({"user_id": user_id})
    unlimited = user_doc.get("unlimited", 0) if user_doc else 0

    today_count = await db.messages.count_documents({
        "user_id": user_id,
        "date": {"$gte": today_start}
    })

    remaining = "♾️ Cheksiz" if unlimited else max(0, 20 - today_count)

    return {
        "unlimited": bool(unlimited),
        "today_count": today_count,
        "remaining": remaining
    }

# ✅ Admin: Cheksiz limit belgilash yoki olib tashlash
async def set_user_unlimited(user_id: int, status: bool):
    result = await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"unlimited": int(status)}}
    )
    return result.modified_count > 0

# ✅ Foydalanuvchini ID orqali olish
async def get_user_by_id(user_id: int):
    return await db.users.find_one({"user_id": user_id})

# ✅ Cheksiz limitli foydalanuvchilar ro‘yxati
async def get_unlimited_users():
    cursor = db.users.find({"unlimited": 1})
    return [user async for user in cursor]
