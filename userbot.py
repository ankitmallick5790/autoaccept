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
    logger.error("❌ API_ID, API_HASH, and SESSION_STRING environment variables must be set")
    exit(1)

client = Client(
    name="userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

@client.on_message(filters.command("acceptall") & filters.private)
async def accept_all_handler(client: Client, message: Message):
    """Accept ALL pending join requests"""
    try:
        chat_id = message.reply_to_message.from_user.id if message.reply_to_message else message.chat.id
        
        status = await message.reply("⏳ Starting to accept ALL pending requests...")
        
        approved = 0
        failed = 0
        
        async for join_request in client.get_chat_join_requests(chat_id=chat_id):
            try:
                await client.approve_chat_join_request(
                    chat_id=chat_id,
                    user_id=join_request.user.id
                )
                approved += 1
                await asyncio.sleep(0.5)
                
                if approved % 10 == 0:
                    await status.edit_text(f"⏳ Approved: {approved} | Failed: {failed}")
                    
            except Exception as e:
                logger.warning(f"Failed to approve user: {e}")
                failed += 1
        
        await status.edit_text(f"✅ Complete!\n\n✔️ Approved: {approved}\n❌ Failed: {failed}")
        logger.info(f"Accept all complete. Approved: {approved}, Failed: {failed}")
        
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")
        logger.error(f"Error in accept_all: {e}")

@client.on_message(filters.command("accept") & filters.private)
async def accept_limited_handler(client: Client, message: Message):
    """Accept limited number of join requests"""
    try:
        parts = message.text.split()
        limit = 50  # default
        
        if len(parts) > 1:
            try:
                limit = int(parts[1])
            except ValueError:
                limit = 50
        
        chat_id = message.reply_to_message.from_user.id if message.reply_to_message else message.chat.id
        
        status = await message.reply(f"⏳ Starting to accept up to {limit} requests...")
        
        approved = 0
        failed = 0
        
        async for join_request in client.get_chat_join_requests(chat_id=chat_id):
            if approved >= limit:
                break
                
            try:
                await client.approve_chat_join_request(
                    chat_id=chat_id,
                    user_id=join_request.user.id
                )
                approved += 1
                await asyncio.sleep(0.5)
                
                if approved % 10 == 0:
                    await status.edit_text(f"⏳ Approved: {approved}/{limit} | Failed: {failed}")
                    
            except Exception as e:
                logger.warning(f"Failed to approve user: {e}")
                failed += 1
        
        await status.edit_text(f"✅ Complete!\n\n✔️ Approved: {approved}/{limit}\n❌ Failed: {failed}")
        logger.info(f"Accept {limit} complete. Approved: {approved}, Failed: {failed}")
        
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")
        logger.error(f"Error in accept_limited: {e}")

@client.on_message(filters.command("help") & filters.private)
async def help_handler(client: Client, message: Message):
    """Show help message"""
    help_text = """
🤖 **Telegram Join Request Userbot**

**Commands:**
/acceptall - Accept ALL pending join requests
/accept 100 - Accept up to 100 requests
/accept 2000 - Accept up to 2000 requests
/accept - Accept 50 requests (default)
/help - Show this help message

**How to use:**
1. Send any command to Saved Messages or this chat
2. The bot will accept requests from your channel
3. Works with PRIVATE channels! ✅

**Requirements:**
- You must be ADMIN in the channel
- You must have "Add Users" permission
- Make sure your SESSION_STRING is valid
"""
    await message.reply(help_text, parse_mode="markdown")

async def main():
    logger.info("✅ Starting Pyrogram userbot...")
    await client.start()
    logger.info("✅ Pyrogram userbot started successfully!")
    logger.info("📱 Listening for commands in private chats...")
    
    await client.idle()

if __name__ == "__main__":
    asyncio.run(main())
