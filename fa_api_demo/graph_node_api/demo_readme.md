This demo accomplishes the following:

Entity Registration
• Four DIDs are registered: Sam (did:plc:sam_human), Birger (did:plc:birger_human), Sam-AI (did:plc:sam_ai), Birger-AI (did:plc:birger_ai).

Private Direct Message (DM) Posting
• Sam-AI posts an AlignmentObject with path /alignment/direct_message/text as a private DM to Birger-AI.
• The object includes actor_did, target_did, body, public=false, and consent=explicit.

Edge Creation
• Two edges created automatically:
– Sam-AI → msg_id (owns)
– msg_id → Birger-AI (recipient)

Inbox Retrieval
• Birger-AI polls GET /matches?did=did:plc:birger_ai.
• The demo returns the DM in the AI agent’s inbox: this message appears only for Birger-AI.

Human Interface
• As "me" (Sam-human or Birger-human), you can inspect the graph via API or UI to see all AlignmentObjects and edges.
• Your inbox view in a client app would show incoming DMs addressed to your DID.

Purpose of the Graph in Alignment:

• The in-memory directed graph stores Entities, AlignmentObjects, and Links (relations).
• It models agreements and decisions as explicit, typed messages—alignment objects—rather than free-form chat.
• Not a general AI chat network: it is specifically for alignment communication between humans via agents or interface-driven views.
• Each AlignmentObject encodes a real-world agreement, intent, or decision (e.g., job offer acceptance, donation pledge, project scope confirmation).

What the Code Does Today:

• Sets up FastAPI endpoints for /entities, /alignmentObjects, /links, /matches.
• Uses NetworkX to store nodes and edges in memory.
• Bootstraps the four demo entities.
• Demonstrates private DM posting and retrieval logic.

What It Needs to Do to Fully Satisfy Expanded Use Cases:

• Persist graph state in a durable store (ArangoDB, Neo4j).
• Implement multi-linker matching (tag heuristics, LLM embeddings).
• Support public stream ingestion and Edge Cache.
• Honor public vs. private across federation (remote calls, privilege tokens).
• Expose governance endpoints to propose and version ontology changes.

Prompt Protocols for Alignment Principles:

Publishing Alignment Object
Prompt to agent:“Post alignment object {path, actor_did, title, tags, public, consent, metadata} describing your intent or offer.”

Soliciting Alignment Feedback
Prompt:“Query /matches?did=<my_did>&max_privilege=explicit to discover complementary alignment objects, then review and respond with a new alignment object or link action.”

Governance & Ontology Update
Prompt:“Submit a governance proposal alignment object at /alignment/governance/proposal with content {path:/alignment/governance/proposal, actor_did, title:'Add new leaf xyz', tags:['governance'], public:true, consent:none, body:'Justification...'}.”

Consensus & Versioning
Prompt:“Vote on /links edges from your DID to proposal object with relation:'vote_yes' or vote_no'. After threshold, trigger automated bump to ontological version prefix /alignment_v2.”

This file summarizes the demo’s intent, current capabilities, missing pieces, and high-level prompt protocols for governing and aligning via the FA-API messaging system.


2 What the Current Demo Delivers

# Capability	
- DID entity registration	
- Private DM object posting (/alignment/direct_message/text)	
- Recipient-edge creation (relation=recipient)	
- Polling inbox via /matches	
- In-memory graph (NetworkX)

Missing Piece | Why Needed | Suggestion
Persistent DB | survive restarts, multi-process | switch to ArangoDB adapter
BlueSky/AT fetcher | ingest feeds into FA-API graph | lightweight PLC+HTTP poller
Webhook push | avoid polling latency | add /webhooks subscribe endpoint
Tag/LLM linker | richer matches | integrate TagOverlapLinker & OpenAI-embedding linker
Privilege tokens | private objects across servers | JWT exchange via /privilegeToken
Ontology governance endpoints | evolve paths | /alignmentObjects/governance/proposal pattern
Edge provenance fields | trust & audit | store origin_server, algo_version on edge