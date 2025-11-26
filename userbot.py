import asyncio
import os
import logging
from flask import Flask, request
from pyrogram import Client

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get environment variables
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
SESSION_STRING = os.getenv("SESSION_STRING", "")

if not (API_ID and API_HASH and SESSION_STRING):
    logger.error("❌ API_ID, API_HASH, and SESSION_STRING environment variables must be set")
    exit(1)

app = Flask(__name__)
client = Client(
    name="userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

@app.route("/", methods=["GET"])
def home():
    return {"status": "Telegram Userbot is running"}

@app.route("/accept", methods=["POST"])
def accept_requests():
    """Accept join requests in a channel"""
    data = request.json
    if not data or "channel" not in data:
        return {"error": "Missing required 'channel' field"}, 400

    channel = data["channel"]
    limit = data.get("limit")

    async def process():
        approved = 0
        failed = 0
        try:
            async for join_request in client.get_chat_join_requests(chat_id=channel):
                if limit is not None and approved >= limit:
                    break
                try:
                    await client.approve_chat_join_request(
                        chat_id=channel,
                        user_id=join_request.user.id
                    )
                    approved += 1
                    await asyncio.sleep(0.5)
                except Exception as e:
                    logger.warning(f"Failed to approve user: {e}")
                    failed += 1
        except Exception as e:
            logger.error(f"Error: {e}")
            return {"error": str(e)}

        return {"approved": approved, "failed": failed}

    future = asyncio.run_coroutine_threadsafe(process(), client.loop)
    try:
        result = future.result(timeout=60)
        return result
    except Exception as e:
        return {"error": str(e)}, 500

def run_flask():
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

def main():
    logger.info("✅ Starting Pyrogram client...")
    client.start()
    logger.info("✅ Pyrogram client started successfully")
    logger.info(f"✅ Flask running on port {os.getenv('PORT', 5000)}")
    run_flask()

if __name__ == "__main__":
    main()
