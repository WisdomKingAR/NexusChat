import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "nexuschat_v3")

async def cleanup():
    print(f"Connecting to {MONGO_URL}...")
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Clean rooms
    print("Deleting rooms...")
    await db.rooms.delete_many({})
    
    # Clean messages
    print("Deleting messages...")
    await db.messages.delete_many({})
    
    # Clean DM channels
    print("Deleting DM channels...")
    await db.dm_channels.delete_many({})
    
    # Clean DM messages
    print("Deleting DM messages...")
    await db.dm_messages.delete_many({})
    
    # Clean users
    print("Deleting users...")
    await db.users.delete_many({})
    
    print("Cleanup complete.")
    client.close()

if __name__ == "__main__":
    asyncio.run(cleanup())
