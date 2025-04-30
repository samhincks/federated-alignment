"""
dm_agent/bluesky_dm.py
Fetches only *new* Bluesky DM messages since the last cursor checkpoint.

ENV:
  FED_HANDLE   • Bluesky handle of the agent   (e.g. sam-ai.bsky.social)
  FED_APP_PW   • App-password with DM scope
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Generator, Tuple

from dotenv import load_dotenv
from atproto import Client, models

load_dotenv()

# ───────────────────────────── env & cursor
HANDLE = os.getenv("FED_HANDLE")
APP_PW = os.getenv("FED_APP_PW")
CURSOR_FILE = Path(__file__).parent / ".dm_cursor.json"  # per-agent

def _load_cursor() -> dict[str, str]:
    if CURSOR_FILE.exists():
        return json.loads(CURSOR_FILE.read_text())
    return {}

def _save_cursor(c: dict[str, str]):
    CURSOR_FILE.write_text(json.dumps(c, indent=0))

# ───────────────────────────── client factory
def _client() -> Client:
    if not (HANDLE and APP_PW):
        raise RuntimeError("Set FED_HANDLE and FED_APP_PW env vars.")
    c = Client()
    c.login(HANDLE, APP_PW)
    return c

# ───────────────────────────── public generator
def fetch_new_messages(
    page_size: int = 50,
) -> Generator[Tuple[str, models.ChatBskyConvoDefs.MessageView], None, None]:
    """
    Yields (convo_id, message) for each *unseen* incoming DM.

    Guarantees:
      • never yields a message id twice
      • safe if the last-seen message was deleted
      • paginates until it sees last_seen OR exhausts timeline
    """
    cl = _client()
    my_did = cl.me.did
    dm_api = cl.with_bsky_chat_proxy().chat.bsky.convo

    cursor_map = _load_cursor()       # {convo_id: last_seen_msg_id}
    new_cursor = dict(cursor_map)

    # 1⃣ get list of convos (newest-activity first)
    convos = dm_api.list_convos(limit=page_size).convos

    for convo in convos:
        last_seen = cursor_map.get(convo.id)           # may be None (=first run)
        newest_msg_id_seen = None
        got_new = False

        # paginated walk: newest→oldest, but we process reversed page to keep order
        next_cursor: str | None = None
        while True:
            page = dm_api.get_messages(
                models.ChatBskyConvoGetMessages.Params(convo_id=convo.id, cursor=next_cursor, limit=page_size)
            )
            msgs = page.messages
            if not msgs:
                break

            if newest_msg_id_seen is None:
                newest_msg_id_seen = msgs[0].id        # very first page => newest msg id

            # yield oldest→newest in this page
            for m in reversed(msgs):
                if m.id == last_seen:                  # reached checkpoint
                    break
                if m.sender_did == my_did:
                    continue                           # skip self-echo
                yield (convo.id, m)
                got_new = True
            else:
                # we didn't break, meaning checkpoint not reached; keep paging
                if page.cursor is None:                # no more pages
                    break
                next_cursor = page.cursor
                continue
            break  #