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

HANDLE   = os.getenv("FED_HANDLE")
APP_PW   = os.getenv("FED_APP_PW")
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
        "actor_did": HANDLE,
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




# ─── main loop ────────────────────────────
async def run():
    fetcher = BlueskyDMFetcher(HANDLE, APP_PW)                  # uses env vars

    print(f"🤖 DM agent polling every {POLL_SEC}s")
    while True:
        for convo_id, msg in fetcher.fetch_new_messages():
            print(msg)
            #oid = await post_alignment(msg.text or "", msg.sender_did, path, tags)
            #print("Stored object", oid)
            fetcher.send_reply(convo_id, "Logged your message. Thanks!")
            print("sent reply")
        await asyncio.sleep(POLL_SEC)

if __name__ == "__main__":
    asyncio.run(run())