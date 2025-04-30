"""
DM agent that:
1. pulls new messages via BlueskyDMFetcher
2. routes text → (path,tags)
3. POSTs AlignmentObject to local FA-API node
4. replies with a courtesy DM
"""

from __future__ import annotations
import asyncio, os
from datetime import datetime

import httpx
from dotenv import load_dotenv
from atproto import Client, models

from dm_agent.bluesky_dm import BlueskyDMFetcher

load_dotenv()

AI_DID = os.getenv("AI_DID")
FAAPI_URL = os.getenv("FAAPI_URL", "http://localhost:8000")
POLL_SEC = 10

# ─── router (stub) ─────────────────────────
def route(text: str):
    if "license" in text.lower():
        return "/alignment/governance/open_source_license", ["license", "governance"]
    return "/alignment/direct_message/text", ["dm"]

# ─── post to graph ─────────────────────────
async def post_alignment(text, sender, path, tags):
    payload = {
        "actor_did": AI_DID,
        "path": path,
        "label": text[:140],
        "tags": tags,
        "public": False,
        "consent": "explicit",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "body": text,
        "author_did": sender,
    }
    async with httpx.AsyncClient() as x:
        r = await x.post(f"{FAAPI_URL}/alignmentObjects", json=payload)
        r.raise_for_status()
        return r.json()["id"]

# ─── reply helper ─────────────────────────
def _reply_client() -> Client:
    c = Client()
    c.login(os.getenv("FED_HANDLE"), os.getenv("FED_APP_PW"))
    return c

async def send_reply(dm_api, convo_id, text):
    dm_api.send_message(
        models.ChatBskyConvoSendMessage.Data(
            convo_id=convo_id,
            message=models.ChatBskyConvoDefs.MessageInput(text=text),
        )
    )

# ─── main loop ────────────────────────────
async def run():
    if not AI_DID:
        raise SystemExit("Set AI_DID env var.")

    fetcher = BlueskyDMFetcher()                   # uses env vars
    dm_api  = _reply_client().with_bsky_chat_proxy().chat.bsky.convo

    print(f"🤖 DM agent polling every {POLL_SEC}s")
    while True:
        for convo_id, msg in fetcher.fetch_new_messages():
            path, tags = route(msg.text or "")
            oid = await post_alignment(msg.text or "", msg.sender_did, path, tags)
            print("Stored object", oid)
            await send_reply(dm_api, convo_id, "Logged your message. Thanks!")
        await asyncio.sleep(POLL_SEC)

if __name__ == "__main__":
    asyncio.run(run())