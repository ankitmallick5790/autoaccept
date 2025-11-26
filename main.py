import asyncio
import os
import logging
from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager

# Userbot code (paste your fixed userbot code here)
from userbot import client  # Import the client from your userbot file

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - start userbot
    logger.info("🚀 Starting userbot...")
    await client.start()
    logger.info("✅ Userbot started successfully!")
    yield
    # Shutdown - stop userbot
    logger.info("🛑 Stopping userbot...")
    await client.stop()
    logger.info("✅ Userbot stopped")

# Create FastAPI app
app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"status": "Userbot running", "service": "join-request-acceptor"}

@app.get("/health")
async def health():
    return {"status": "healthy", "userbot": "active"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
