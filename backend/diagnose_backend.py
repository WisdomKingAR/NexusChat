import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

async def diagnose():
    load_dotenv()
    mongo_url = os.getenv("MONGO_URL")
    db_name = os.getenv("DB_NAME", "nexuschat_v3")
    cors_origins = os.getenv("CORS_ORIGINS")
    
    print(f"\n--- Backend Diagnostics ---")
    print(f"MONGO_URL: {mongo_url}")
    print(f"DB_NAME: {db_name}")
    print(f"CORS_ORIGINS: {cors_origins}")
    
    if not mongo_url:
        print("ERROR: MONGO_URL not found in environment.")
        return

    print(f"\nTesting MongoDB Connection (2s timeout)...")
    client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=2000)
    try:
        # Check if server is available
        await client.admin.command('ismaster')
        print("SUCCESS: Connected to MongoDB successfully!")
        
        # Check if database is accessible
        db = client[db_name]
        collections = await db.list_collection_names()
        print(f"SUCCESS: Database '{db_name}' is accessible. Collections: {collections}")
    except Exception as e:
        print(f"FAILURE: Could not connect to MongoDB: {e}")

if __name__ == "__main__":
    asyncio.run(diagnose())
