import asyncio
import os
import logging
from pyrogram import Client, filters
from pyrogram.types import Message

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
SESSION_STRING = os.getenv("SESSION_STRING", "")

if not (API_ID and API_HASH and SESSION_STRING):
    logger.error("❌ Missing env vars")
    raise ValueError("Missing API_ID, API_HASH, or SESSION_STRING")

client = Client(
    name="userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

@client.on_message(filters.command("acceptall") & filters.private)
async def accept_all_handler(client: Client, message: Message):
    try:
        chat_id = message.reply_to_message.chat.id if message.reply_to_message else message.chat.id
        status = await message.reply("⏳ Starting to accept ALL pending requests...")
        
        approved = 0
        failed = 0
        
        async for join_request in client.get_chat_join_requests(chat_id=chat_id):
            try:
                await client.approve_chat_join_request(chat_id=chat_id, user_id=join_request.user.id)
                approved += 1
                await asyncio.sleep(0.5)
                if approved % 10 == 0:
                    await status.edit_text(f"⏳ Approved: {approved} | Failed: {failed}")
            except Exception as e:
                logger.warning(f"Failed to approve: {e}")
                failed += 1
        
        await status.edit_text(f"✅ Complete!\n✔️ Approved: {approved}\n❌ Failed: {failed}")
        
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")

@client.on_message(filters.command("accept") & filters.private)
async def accept_limited_handler(client: Client, message: Message):
    try:
        parts = message.text.split()
        limit = int(parts[1]) if len(parts) > 1 else 50
        
        chat_id = message.reply_to_message.chat.id if message.reply_to_message else message.chat.id
        status = await message.reply(f"⏳ Accepting up to {limit} requests...")
        
        approved = 0
        failed = 0
        
        async for join_request in client.get_chat_join_requests(chat_id=chat_id):
            if approved >= limit:
                break
            try:
                await client.approve_chat_join_request(chat_id=chat_id, user_id=join_request.user.id)
                approved += 1
                await asyncio.sleep(0.5)
            except Exception as e:
                failed += 1
        
        await status.edit_text(f"✅ Complete!\n✔️ Approved: {approved}/{limit}\n❌ Failed: {failed}")
        
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")

@client.on_message(filters.command("help") & filters.private)
async def help_handler(client: Client, message: Message):
    help_text = """
🤖 **Join Request Userbot**

/acceptall - Accept ALL requests
/accept 100 - Accept up to 100
/help - This message
    """
    await message.reply(help_text)
