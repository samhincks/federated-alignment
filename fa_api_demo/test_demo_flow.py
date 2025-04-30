from fastapi.testclient import TestClient
from app import main

client = TestClient(main.app)


def test_dm_and_broadcast_flow():
    # Sam-AI sends a private DM to Birger-AI
    dm = {
        "path": "/alignment/open_source/direct_message",
        "actor_did": "did:example:sam-ai",
        "label": "Ping Birger",
        "tags": ["dm"],
        "public": False,
        "consent": "explicit",
        "target_did": "did:example:birger-ai",
        "body": "Hello Birger!"
    }
    r = client.post("/alignmentObjects", json=dm)
    assert r.status_code == 200
    dm_id = r.json()["id"]

    # Birger-AI polls matches and should receive the DM
    res = client.get("/matches", params={"did": "did:example:birger-ai"})
    assert any(m["id"] == dm_id for m in res.json()["results"])

    # Sam-AI's open-source alignment object should have been broadcast to Birger-AI
    assert main.G.has_edge(
        "alignobj:federated_alignment_api_v0",
        "did:example:birger-ai"
    )