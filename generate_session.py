import asyncio
from pyrogram import Client

API_ID = 24286461  # Your API ID from my.telegram.org
API_HASH = "fe4f9e040dfefaeb8715e12d1e4da9de"  # Your API Hash from my.telegram.org

async def main():
    async with Client("my_account", api_id=API_ID, api_hash=API_HASH) as app:
        session_string = await app.export_session_string()
        print("\n" + "="*60)
        print("✅ SESSION STRING GENERATED SUCCESSFULLY!")
        print("="*60)
        print("\n📋 Copy this SESSION_STRING:\n")
        print(session_string)
        print("\n" + "="*60)
        print("⚠️  Keep this secret! Don't share it with anyone!")
        print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
