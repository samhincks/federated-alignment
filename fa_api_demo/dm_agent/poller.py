"""
poller.py – DM agent that:
1. pulls new messages via bluesky_dm.fetch_new_messages()
2. routes text → (path,tags)  [stub]
3. POSTs AlignmentObject  to local FA-API node
4. replies with a courtesy DM
"""

from __future__ import annotations
import asyncio, os
from datetime import datetime
import httpx

from dotenv import load_dotenv
from atproto import Client, models

from .bluesky_dm import fetch_new_messages   # ← our helper

load_dotenv()

AI_DID    = os.getenv("AI_DID")
FAAPI_URL = os.getenv("FAAPI_URL", "http://localhost:8000")
POLL_SEC  = 10


async def post_alignment(text: str, sender_did: str, path: str, tags: list[str]) -> str:
    payload = {
        "actor_did": AI_DID,
        "path": path,
        "label": text[:140],
        "tags": tags,
        "public": False,
        "consent": "explicit",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "body": text,
        "author_did": sender_did,
    }
    async with httpx.AsyncClient() as x:
        r = await x.post(f"{FAAPI_URL}/alignmentObjects", json=payload, timeout=10)
        r.raise_for_status()
        return r.json()["id"]


def route(text: str) -> tuple[str, list[str]]:
    """
    Stub router: license question → governance path, else generic DM path.
    Replace with smarter NLP later.
    """
    if "license" in text.lower():
        return ("/alignment/governance/open_source_license", ["license", "governance"])
    return ("/alignment/direct_message/text", ["dm"])


async def dm_reply(dm_api, convo_id: str, text: str):
    dm_api.send_message(
        models.ChatBskyConvoSendMessage.Data(
            convo_id=convo_id,
            message=models.ChatBskyConvoDefs.MessageInput(text=text),
        )
    )


async def run():
    if not AI_DID:
        raise SystemExit("Set AI_DID env var.")

    # Need a client to send replies; reuse bluesky_dm._client()
    from .bluesky_dm import _client
    reply_client = _client()
    dm_api = reply_client.with_bsky_chat_proxy().chat.bsky.convo

    print(f"🤖 DM agent started – polling every {POLL_SEC}s")
    while True:
        for convo_id, msg in fetch_new_messages():
            path, tags = route(msg.text or "")
            obj_id = await post_alignment(msg.text or "", msg.sender_did, path, tags)
            print(f"📝 Stored AlignmentObject {obj_id}")

            await dm_reply(
                dm_api,
                convo_id,
                f"Logged your message into the alignment graph (node {obj_id[:8]}…). Thanks!",
            )
        await asyncio.sleep(POLL_SEC)


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("bye")