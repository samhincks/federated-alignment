import fnmatch
import uuid
import networkx as nx
from fastapi import FastAPI, HTTPException
from graph_node_api.schemas import EntityIn, AlignmentObjectIn, Relation
from graph_node_api.logic import load_graph, save_graph

app = FastAPI(title="FA-API MVP")
G: nx.DiGraph = load_graph()   # survives restarts


# ──────────────────────────────── graph helpers
def add_entity(ent: EntityIn):
    G.add_node(ent.did, **ent.model_dump())
    if ent.controls:
        G.add_edge(ent.controls, ent.did, relation=Relation.controls)


def add_alignment(obj: AlignmentObjectIn) -> str:
    obj_id = obj.label.lower().replace(" ", "_") + "_" + uuid.uuid4().hex[:6]
    G.add_node(obj_id, **obj.model_dump())
    G.add_edge(obj.actor_did, obj_id, relation=Relation.author_of)
    if obj.target_did:  # DM variant
        G.add_edge(obj_id, obj.target_did, relation=Relation.recipient)
    return obj_id


def broadcast(obj_id: str):
    """For each AI whose subscriptions pattern-match, create context_push edge."""
    obj_path = G.nodes[obj_id]["path"]
    for ai, data in G.nodes(data=True):
        if data.get("type") == "AI":
            for pattern in data.get("subscriptions", []):
                if fnmatch.fnmatch(obj_path, pattern):
                    if not G.has_edge(obj_id, ai):
                        G.add_edge(obj_id, ai, relation=Relation.context_push)


# ──────────────────────────────── FastAPI routes
@app.post("/entities")
def post_entity(ent: EntityIn):
    add_entity(ent)
    save_graph(G)
    return {"status": "ok", "did": ent.did}


@app.post("/alignmentObjects")
def post_alignment(obj: AlignmentObjectIn):
    if not G.has_node(obj.actor_did):
        raise HTTPException(404, "actor DID not registered")
    obj_id = add_alignment(obj)
    broadcast(obj_id)
    save_graph(G)
    return {"status": "created", "id": obj_id}


@app.get("/matches")
def get_matches(did: str):
    if not G.has_node(did):
        raise HTTPException(404, "unknown DID")

    results = []
    for src, _, e in G.in_edges(did, data=True):
        if e["relation"] in {Relation.context_push, Relation.recipient}:
            body = G.nodes[src].get("body")
            results.append({"id": src, "body": body, "score": 1})
    return {"subject": did, "results": results}