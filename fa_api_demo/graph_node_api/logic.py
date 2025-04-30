"""
Graph persistence helpers.
"""
import json
import pathlib
import networkx as nx

DB_FILE = pathlib.Path(__file__).parent / "db.json"


# ───────────────────────────────────────── I/O helpers
def load_graph() -> nx.DiGraph:
    G = nx.DiGraph()
    if not DB_FILE.exists():
        return G

    doc = json.loads(DB_FILE.read_text())

    # Nodes
    for ent in doc.get("entities", []):
        G.add_node(ent["did"], **ent)
    for obj in doc.get("alignment_objects", []):
        G.add_node(obj["id"], **obj)

    # Edges
    for e in doc.get("edges", []):
        G.add_edge(e["_from"], e["_to"], relation=e["relation"])

    return G


def save_graph(G: nx.DiGraph):
    out = {"entities": [], "alignment_objects": [], "edges": []}

    for n, data in G.nodes(data=True):
        if data.get("type"):              # Entity
            out["entities"].append(data)
        elif data.get("path"):            # AlignmentObject
            out["alignment_objects"].append(data)

    for u, v, e in G.edges(data=True):
        out["edges"].append({"_from": u, "_to": v, "relation": e["relation"]})

    DB_FILE.write_text(json.dumps(out, indent=2))