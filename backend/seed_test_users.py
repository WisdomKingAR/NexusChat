import asyncio
import os
import bcrypt
import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

async def ensure_admin():
    mongo_url = os.getenv("MONGO_URL")
    db_name = os.getenv("DB_NAME", "nexuschat_v3")
    client = AsyncIOMotorClient(mongo_url, tlsCAFile=certifi.where())
    db = client[db_name]
    
    email = "admin@test.com"
    password = "Test@123"
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    user = await db.users.find_one({"email": email})
    if user:
        await db.users.update_one(
            {"email": email},
            {"$set": {"role": "admin", "password_hash": hashed}}
        )
        print(f"Updated user {email} to admin with correct password.")
    else:
        await db.users.insert_one({
            "email": email,
            "display_name": "Admin",
            "password_hash": hashed,
            "role": "admin",
            "created_at": datetime.now(timezone.utc)
        })
        print(f"Created admin user {email}.")
    
    # Also ensure there's a moderator for the /demote test
    mod_email = "mod@test.com"
    mod_user = await db.users.find_one({"email": mod_email})
    if not mod_user:
        await db.users.insert_one({
            "email": mod_email,
            "display_name": "ModeratorUser",
            "password_hash": hashed,
            "role": "moderator",
            "created_at": datetime.now(timezone.utc)
        })
        print(f"Created moderator user {mod_email}.")

if __name__ == "__main__":
    asyncio.run(ensure_admin())
