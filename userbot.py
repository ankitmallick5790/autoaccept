import asyncio
import os
import logging
from flask import Flask, request
from pyrogram import Client, enums

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
    logger.error("API_ID, API_HASH, and SESSION_STRING environment variables must be set")
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
    return "Telegram Join Request Userbot is running."

@app.route("/accept", methods=["POST"])
def accept_requests():
    """
    Accept join requests in a channel.
    POST JSON body must contain:
      - channel (str): channel ID (int as str or -1001234567890) or username (@username)
      - limit (int, optional): max number of requests to approve, default all
    """
    data = request.json
    if not data or "channel" not in data:
        return {"error": "Missing required 'channel' field"}, 400

    channel = data["channel"]
    limit = data.get("limit")  # can be None

    async def process():
        approved = 0
        failed = 0
        try:
            # Iterate over join requests for the channel
            async for join_request in client.get_chat_join_requests(chat_id=channel):
                if limit is not None and approved >= limit:
                    break
                try:
                    await client.approve_chat_join_request(chat_id=channel, user_id=join_request.user.id)
                    approved += 1
                    await asyncio.sleep(0.5)  # respectful delay to avoid flood
                except Exception as e:
                    logger.warning(f"Failed to approve user {join_request.user.id}: {e}")
                    failed += 1
        except Exception as e:
            logger.error(f"Error fetching join requests: {e}")
            return {"error": str(e)}

        return {"approved": approved, "failed": failed}

    future = asyncio.run_coroutine_threadsafe(process(), client.loop)
    result = future.result(timeout=60)
    return result

def run_flask():
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

def main():
    client.start()
    logger.info("Pyrogram client started")
    run_flask()

if __name__ == "__main__":
    main()
