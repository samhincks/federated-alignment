"""
Utility: BlueskyDMFetcher
Logs into Bluesky and yields ONLY new DMs since last cursor.
Logic is IDENTICAL to your function; just wrapped in a class.
"""

from __future__ import annotations
import json, os
from pathlib import Path
from typing import List, Tuple

from dotenv import load_dotenv
from atproto import Client, models

load_dotenv()

HANDLE = os.getenv("FED_HANDLE")   # sam-ai.bsky.social
APP_PW = os.getenv("FED_APP_PW")   # app password (DM scope)


class BlueskyDMFetcher:
    def __init__(
        self,
        handle: str = HANDLE,
        app_pw: str = APP_PW,
        cursor_file: Path | None = None,
    ):
        if not (handle and app_pw):
            raise RuntimeError("FED_HANDLE / FED_APP_PW env vars missing")
        self.handle = handle
        self.app_pw = app_pw
        self.cursor_file = (
            cursor_file
            if cursor_file
            else Path(__file__).parent / ".dm_cursor.json"
        )

        # Lazily created client
        self._client: Client | None = None

    # ─── helpers (IDENTICAL logic) ────────────────────────────────
    def _load_cursor(self) -> dict[str, str]:
        if self.cursor_file.exists():
            return json.loads(self.cursor_file.read_text())
        return {}

    def _save_cursor(self, c: dict[str, str]):
        self.cursor_file.write_text(json.dumps(c))

    def _client_logged_in(self) -> Client:
        if self._client is None:
            cl = Client()
            cl.login(self.handle, self.app_pw)
            self._client = cl
        return self._client

    # ─── public API ───────────────────────────────────────────────
    def fetch_new_messages(
        self,
    ) -> List[Tuple[str, models.ChatBskyConvoDefs.MessageView]]:
        """
        Returns list[(convo_id, message)] for each *unseen* incoming message.
        (Logic matches your original procedural function.)
        """
        client = self._client_logged_in()
        dm_api = client.with_bsky_chat_proxy().chat.bsky.convo

        cursor = self._load_cursor()        # {convo_id: last_msg_id}
        new_cursor = dict(cursor)

        results: list[Tuple[str, models.ChatBskyConvoDefs.MessageView]] = []

        convo_list = dm_api.list_convos()

        for convo in convo_list.convos:
            last_seen = cursor.get(convo.id)
            msgs = dm_api.get_messages(
                models.ChatBskyConvoGetMessages.Params(convo_id=convo.id)
            )
            unseen_msgs = []

            # walk oldest→newest so order is preserved
            for m in msgs.messages:
                print("last seen", last_seen)
                print("m", m.id)

                if m.id == last_seen:
                    break
                unseen_msgs.append(m)

            for m in unseen_msgs:
                results.append((convo.id, m))

            if msgs.messages:  # messages[0] is newest
                new_cursor[convo.id] = msgs.messages[0].id

        self._save_cursor(new_cursor)
        return results