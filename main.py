import asyncio
import os
import logging
from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Import AFTER logging setup
from userbot import client

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting Telegram Userbot...")
    try:
        await client.start()
        logger.info("✅ Userbot STARTED - Send /help to Saved Messages!")
        yield
    except Exception as e:
        logger.error(f"❌ Userbot failed to start: {e}")
        raise
    finally:
        logger.info("🛑 Stopping Userbot...")
        await client.stop()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"status": "✅ Userbot Running", "commands": ["/help", "/acceptall", "/accept 50"]}

@app.get("/health")
async def health():
    return {"status": "healthy", "userbot": "active"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False, log_level="info")
