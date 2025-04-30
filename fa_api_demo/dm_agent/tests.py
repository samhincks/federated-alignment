from dm_agent.bluesky_dm import BlueskyDMFetcher

def test_poll_twice():
    fetcher = BlueskyDMFetcher()
    print("── Run #1, make sure dm_cursor.json is deleted for test")
    first = fetcher.fetch_new_messages()
    for cid, m in first:
        print("NEW:", cid[:6], m.text)

    print("\n── Run #2 (immediate)")
    second = fetcher.fetch_new_messages()
    if second:
        print("❌ duplicates:", second)
    else:
        print("✅ No new messages (as expected)")

if __name__ == "__main__":
    test_poll_twice()