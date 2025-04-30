# dm_agent/test_fetch_dms.py

from dm_agent.bluesky_dm import fetch_new_messages

def test_poll_once():
    new_messages = list(fetch_new_messages())

    if not new_messages:
        print("✅ No new messages (expected if quiet).")
    else:
        for convo_id, msg in new_messages:
            print(f"🆕 DM: convo={convo_id}, text='{msg.text}'")

if __name__ == "__main__":
    test_poll_once()