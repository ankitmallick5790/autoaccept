import asyncio
import os
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, ChatAdminRequired, UserPrivacyRestricted

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
SESSION_STRING = os.getenv("SESSION_STRING", "")

if not all([API_ID, API_HASH, SESSION_STRING]):
    logger.error("❌ Missing API_ID, API_HASH, or SESSION_STRING")
    raise ValueError("Missing environment variables")

# Create client
client = Client(
    name="userbot-render",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

@client.on_message(filters.private & filters.command("start"))
async def start_cmd(client: Client, message: Message):
    await message.reply("🤖 **Userbot Active!**\n\nUse:\n/help - Commands\n/acceptall - Accept ALL\n/accept 50 - Accept 50")

@client.on_message(filters.private & filters.command("help"))
async def help_cmd(client: Client, message: Message):
    help_text = """
🤖 **Join Request Userbot** ✅

**Commands:**
• `/acceptall` - Accept ALL pending requests
• `/accept 50` - Accept 50 requests (change number)
• `/help` - Show this message

**How to use:**
1. Reply to channel message OR send to Saved Messages
2. Bot accepts requests from that channel
3. Works on PRIVATE channels too! 🔓

**Must be:** Channel ADMIN with "Add Users" permission
    """
    await message.reply(help_text)

@client.on_message(filters.private & filters.command("acceptall"))
async def accept_all(client: Client, message: Message):
    chat_id = message.reply_to_message.chat.id if message.reply_to_message else message.chat.id
    
    status = await message.reply("⏳ Accepting **ALL** join requests...")
    
    approved, failed = 0, 0
    
    try:
        async for request in client.get_chat_join_requests(chat_id):
            try:
                await client.approve_chat_join_request(chat_id, request.user.id)
                approved += 1
                await asyncio.sleep(1)  # Rate limit
                
                if approved % 10 == 0:
                    await status.edit_text(f"⏳ Approved: **{approved}** | Failed: {failed}")
                    
            except FloodWait as e:
                logger.warning(f"FloodWait: {e.value} seconds")
                await asyncio.sleep(e.value)
            except (ChatAdminRequired, UserPrivacyRestricted):
                failed += 1
            except Exception as e:
                logger.warning(f"Failed request: {e}")
                failed += 1
        
        await status.edit_text(
            f"✅ **Complete!**\n\n"
            f"✔️ **Approved:** {approved}\n"
            f"❌ **Failed:** {failed}"
        )
        
    except Exception as e:
        await status.edit_text(f"❌ Error: {str(e)}")

@client.on_message(filters.private & filters.command("accept"))
async def accept_limit(client: Client, message: Message):
    try:
        parts = message.text.split()
        limit = int(parts[1]) if len(parts) > 1 else 50
        
        chat_id = message.reply_to_message.chat.id if message.reply_to_message else message.chat.id
        
        status = await message.reply(f"⏳ Accepting up to **{limit}** requests...")
        
        approved, failed = 0, 0
        
        async for request in client.get_chat_join_requests(chat_id):
            if approved >= limit:
                break
                
            try:
                await client.approve_chat_join_request(chat_id, request.user.id)
                approved += 1
                await asyncio.sleep(1)
                
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception:
                failed += 1
        
        await status.edit_text(
            f"✅ **Complete!**\n\n"
            f"✔️ **Approved:** {approved}/{limit}\n"
            f"❌ **Failed:** {failed}"
        )
        
    except ValueError:
        await message.reply("❌ Usage: `/accept 50`")
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")

# Debug - log all private messages
@client.on_message(filters.private)
async def debug_msg(client: Client, message: Message):
    if message.text:
        logger.info(f"📨 Private message: {message.text[:50]}...")
