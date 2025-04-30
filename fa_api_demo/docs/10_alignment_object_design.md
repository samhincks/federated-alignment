Aspect | Description
Payload | A formalized intent — need, offer, proposal, vote, message, etc.
Schema anchor | path points to a stable leaf in the ontology → guarantees every consumer knows how to interpret the object without extra metadata.
Inter-actor contract | Carries all state needed to complete or advance an alignment cycle (who, what, status, consent).
Machine-first | Parsable by graph engines and matchers; stored as a vertex with minimal required fields; optional rich extras (embeddings, links).
Human-recoverable | title + optional body keep it readable; can be rendered in a UI or chat.

free text / chat  ──►  prompt-template  ───►  LLM  ───►  Draft JSON
                                            │
                         validation (pydantic, regex, path-exists)
                                            ▼
                                     AlignmentObject

# Generic Alignment Object Extractor
SYSTEM: You are Alignment-Object-Extractor.
USER: <<<raw text>>>
INSTRUCTIONS:
1. Identify intent category (job_post, dm, offer, etc.)
2. Map to ontology leaf path
3. Produce JSON with {path, actor_did, title, tags, ...}

# 
