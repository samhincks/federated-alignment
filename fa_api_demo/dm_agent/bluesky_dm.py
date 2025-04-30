"""
bluesky_dm.py
─────────────
Utility layer that logs into Bluesky with an App-Password and
yields **only new** DM messages since the last cursor checkpoint.

Env vars it expects:

    FED_HANDLE   = sam-ai.bsky.social
    FED_APP_PW   = xxxx-xxxx-xxxx-xxxx   (App password, DM scope)
"""

from __future__ import annotations
import json, os
from pathlib import Path
from typing import Generator, Tuple

from dotenv import load_dotenv
load_dotenv()
from atproto import Client, models

# env
HANDLE  = os.getenv("FED_HANDLE")
APP_PW  = os.getenv("FED_APP_PW")
CURSOR_FILE = Path(__file__).parent / ".dm_cursor.json"   # per-agent cursor

def _load_cursor() -> dict[str, str]:
    if CURSOR_FILE.exists():
        return json.loads(CURSOR_FILE.read_text())
    return {}

def _save_cursor(c: dict[str, str]):
    CURSOR_FILE.write_text(json.dumps(c))

def _client() -> Client:
    if not (HANDLE and APP_PW):
        raise RuntimeError("Set FED_HANDLE and FED_APP_PW env vars.")
    cl = Client()
    cl.login(HANDLE, APP_PW)
    return cl

def fetch_new_messages() -> list[Tuple[str, models.ChatBskyConvoDefs.MessageView]]:
    """
    Returns a list of (convo_id, message) for each *unseen* incoming message.
    """
    client      = _client()
    dm_client   = client.with_bsky_chat_proxy()
    dm_api      = dm_client.chat.bsky.convo

    cursor = _load_cursor()        # {convo_id: last_msg_id}
    new_cursor = dict(cursor)

    convo_list = dm_api.list_convos()

    results = []
    for convo in convo_list.convos:
        last_seen = cursor.get(convo.id)
        msgs = dm_api.get_messages(models.ChatBskyConvoGetMessages.Params(convo_id=convo.id))
        # walk oldest→newest so order is preserved
        for m in reversed(msgs.messages):
            print(last_seen)
            results.append((convo.id, m))
    return results

    _save_cursor(new_cursor)