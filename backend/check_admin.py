import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['nexuschat_v3']
    admin = await db.users.find_one({'role': 'admin'})
    if admin:
        print(f"Admin Email: {admin['email']}")
    else:
        print("No admin found in the database. The next user to register will be made admin.")

if __name__ == '__main__':
    asyncio.run(main())
