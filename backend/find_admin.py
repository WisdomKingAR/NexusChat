import asyncio
import bcrypt
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

async def reset_password():
    client = AsyncIOMotorClient(os.getenv("MONGO_URL"), serverSelectionTimeoutMS=5000)
    db = client[os.getenv("DB_NAME", "nexuschat_v3")]
    new_hash = bcrypt.hashpw("Test@123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    result = await db.users.update_one({"email": "admin@test.com"}, {"$set": {"password_hash": new_hash}})
    if result.modified_count:
        print("Password reset successfully for admin@test.com")
    else:
        print("User not found or password unchanged.")
    client.close()

asyncio.run(reset_password())
