from pyrogram import Client

API_ID = 24286461  # Your API ID
API_HASH = "fe4f9e040dfefaeb8715e12d1e4da9de"  # Your API Hash

app = Client("my_account", api_id=API_ID, api_hash=API_HASH)

async def main():
    async with app:
        print("\n✅ SESSION STRING:")
        print(await app.export_session_string())
        print("\n📋 Copy the above string and use it in your .env file\n")

app.run(main())
