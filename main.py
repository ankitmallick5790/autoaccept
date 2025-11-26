import os
import asyncio
import logging
from fastapi import FastAPI, BackgroundTasks
from pyrogram import Client
from pyrogram.errors import FloodWait
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

async def process_join_requests():
    """Process all pending join requests"""
    if not client:
        logger.error("Client not initialized")
        return {"status": "error", "message": "Client not ready"}
    
    try:
        # Bulk approve first
        success = await client.approve_all_chat_join_requests(CHANNEL_ID)
        if success:
            logger.info("✅ All pending requests approved via bulk method!")
            return {"status": "success", "method": "bulk", "approved": "all"}
    except Exception as e:
        logger.warning(f"Bulk approve failed: {e}")
    
    # Individual processing with progress tracking
    processed = approved = skipped = 0
    async for joiner in client.get_chat_join_requests(CHANNEL_ID, limit=0):
        try:
            await client.approve_chat_join_request(CHANNEL_ID, joiner.user.id)
            approved += 1
            processed += 1
            logger.info(f"✅ Approved {approved}/{processed}: {joiner.user.first_name}")
            await asyncio.sleep(1.5)  # Rate limit
        except FloodWait as e:
            logger.warning(f"FloodWait: {e.value}s")
            await asyncio.sleep(e.value)
            skipped += 1
        except Exception as e:
            logger.error(f"Failed {joiner.user.id}: {e}")
            skipped += 1
        processed += 1
    
    logger.info(f"✅ Complete! Approved: {approved}, Skipped: {skipped}")
    return {"status": "success", "approved": approved, "skipped": skipped, "total": processed}

@app.on_event("startup")
async def startup_event():
    await init_client()

@app.get("/")
async def root():
    return {"message": "Telegram Join Requests Bot is running!", "status": "ready"}

@app.get("/status")
async def status():
    if client and not client.is_connected:
        return {"status": "disconnected"}
    return {"status": "connected", "channel": CHANNEL_ID}

@app.post("/process")
async def trigger_processing(background_tasks: BackgroundTasks):
    """Trigger join requests processing"""
    background_tasks.add_task(asyncio.create_task, process_join_requests())
    return {"status": "processing_started", "channel": CHANNEL_ID}

@app.get("/process")
async def trigger_processing_get():
    """GET version for manual trigger"""
    result = await process_join_requests()
    return result

@app.get("/debug")
async def debug():
    """Debug: Test connection + channel access"""
    if not client:
        return {"error": "Client not ready"}
    
    try:
        # Test channel access
        chat = await client.get_chat(CHANNEL_ID)
        return {
            "status": "connected",
            "channel": {
                "id": chat.id,
                "title": chat.title,
                "type": chat.type,
                "pending_requests": getattr(chat, 'pending_join_requests', 'unknown')
            }
        }
    except Exception as e:
        return {"error": str(e), "channel_id_used": CHANNEL_ID}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
