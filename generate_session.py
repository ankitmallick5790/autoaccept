from pyrogram import Client

API_ID = 12345678  # Your API ID
API_HASH = "your_api_hash"  # Your API Hash

app = Client("my_account", api_id=API_ID, api_hash=API_HASH)

async def main():
    async with app:
        print("\n✅ SESSION STRING:")
        print(await app.export_session_string())
        print("\n📋 Copy the above string and use it in your .env file\n")

app.run(main())
