import os
import asyncio
import logging
from fastapi import FastAPI, BackgroundTasks
from pyrogram import Client
from pyrogram.errors import FloodWait, PeerIdInvalid
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Telegram Join Requests Bot")
client = None

# Environment variables
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
CHANNEL_ID = os.getenv("CHANNEL_ID")

async def init_client():
    global client
    client = Client(
        "join_requests_bot",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=SESSION_STRING
    )
    await client.start()
    logger.info("✅ Client initialized")

@app.on_event("startup")
async def startup_event():
    await init_client()

@app.get("/")
async def root():
    return {"message": "Telegram Join Requests Bot is running!", "status": "ready"}

@app.get("/status")
async def status():
    global client
    if not client or not await client.is_connected():
        return {"status": "disconnected"}
    return {"status": "connected", "channel": CHANNEL_ID}

@app.get("/debug")
async def debug():
    """Debug: Test channel access"""
    global client
    if not client:
        return {"error": "Client not ready"}
    
    try:
        chat = await client.get_chat(CHANNEL_ID)
        return {
            "status": "connected",
            "channel": {
                "id": chat.id,
                "title": chat.title,
                "type": str(chat.type),
                "username": getattr(chat, 'username', None)
            }
        }
    except Exception as e:
        return {"error": str(e), "channel_id_used": CHANNEL_ID}

async def process_join_requests():
    """Process all pending join requests with peer resolution"""
    global client
    if not client:
        logger.error("Client not ready")
        return {"error": "Client not ready"}
    
    # CRITICAL: Resolve peer first
    try:
        logger.info(f"🔍 Resolving channel {CHANNEL_ID}...")
        chat = await client.get_chat(CHANNEL_ID)
        logger.info(f"✅ Channel resolved: {chat.title} (ID: {chat.id})")
        channel_id = chat.id  # Use resolved ID
    except Exception as e:
        logger.error(f"❌ Cannot access channel: {e}")
        return {"error": f"Cannot access {CHANNEL_ID}: {str(e)}. Join channel first with this account."}
    
    # Try bulk approve first
    try:
        logger.info("🚀 Trying bulk approve...")
        success = await client.approve_all_chat_join_requests(channel_id)
        if success:
            logger.info("✅ All pending requests approved via bulk method!")
            return {"status": "success", "method": "bulk", "channel": chat.title, "approved": "all"}
    except Exception as e:
        logger.warning(f"Bulk approve failed: {e}")
    
    # Individual processing with stats
    processed = approved = skipped = 0
    try:
        logger.info("🔄 Starting individual processing...")
        async for joiner in client.get_chat_join_requests(channel_id, limit=0):
            try:
                await client.approve_chat_join_request(channel_id, joiner.user.id)
                approved += 1
                processed += 1
                logger.info(f"✅ Approved {approved}/{processed}: {joiner.user.first_name or 'NoName'} (@{joiner.user.username or 'nousername'})")
                await asyncio.sleep(1.5)  # Rate limit
            except FloodWait as e:
                logger.warning(f"⏳ FloodWait: {e.value}s")
                await asyncio.sleep(e.value)
                skipped += 1
            except Exception as e:
                logger.error(f"❌ Failed {joiner.user.id}: {e}")
                skipped += 1
            processed += 1
        
        logger.info(f"✅ Processing complete! Approved: {approved}, Skipped: {skipped}, Total: {processed}")
        return {
            "status": "success", 
            "method": "individual",
            "channel": chat.title,
            "approved": approved, 
            "skipped": skipped, 
            "total": processed
        }
    except Exception as e:
        logger.error(f"❌ Processing failed: {e}")
        return {"error": f"Processing failed: {str(e)}"}

@app.post("/process")
async def trigger_processing(background_tasks: BackgroundTasks):
    """Trigger processing in background"""
    background_tasks.add_task(process_join_requests)
    return {"status": "processing_started", "channel": CHANNEL_ID}

@app.get("/process")
async def trigger_processing_get():
    """Process immediately and return results"""
    result = await process_join_requests()
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
