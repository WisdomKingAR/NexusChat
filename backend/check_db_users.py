import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

async def check_users():
    load_dotenv()
    mongo_url = os.getenv("MONGO_URL")
    db_name = os.getenv("DB_NAME", "nexuschat_v3")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    users = await db.users.find().to_list(100)
    print(f"Total users: {len(users)}")
    for user in users:
        print(f"Email: {user['email']}, Role: {user['role']}, ID: {user['_id']}")

if __name__ == "__main__":
    asyncio.run(check_users())
