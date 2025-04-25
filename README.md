📡 Federated Alignment API
A minimal, open protocol for AI-assisted matching between people, projects, and organizations — across ecosystems, platforms, and federated networks.

The Federated Alignment API (FA-API) is a lightweight, extensible specification for expressing and discovering alignment objects — such as job posts, project needs, funding offers, skillsets, or collaboration intents — in a standardized format. Designed to support interoperability between apps, agents, and humans, FA-API connects distributed graphs of “who needs what” and “who offers what,” enabling scalable alignment across use cases.

## Core features
- Shared alignment object schema (needs / offers / archetypes / skills)
- Cross-platform identity via DIDs (e.g. BlueSky, wallets, ActivityPub)
- Consent-aware metadata (public, private, consent_required)
- Modular match algorithms (rules, vectors, LLMs)
- Works with private or public graph stores
- Zero lock-in: anyone can implement, fork, or extend

## Use cases already in development
- 🐠 Ocean regeneration (Your Devocean)
- 👥 AI-driven hiring (Ada Recruitment)

## Use cases considered
- 🧙 Influencer–brand matching
- 🧬 Funder–founder graph alignment
- 🏕️ Retreat & regenerative community matching

This is not a platform. It's a contract.
Anyone can build vertical apps that speak FA-API. The protocol empowers decentralized collaboration, not central ownership.



# What problem is the Federated Alignment API actually solving?
### 🔥 Why This Protocol Exists

| Pain Point                             | Current Workaround                                                       | Why It’s Broken                                                                 |
|----------------------------------------|---------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| Fragmented “need/offer” data (jobs, grants, ESG gigs, talent, carbon credits…) | Thousands of niche SaaS tools, spreadsheets, Discords, emails             | Data silos, no universal search, and everyone rebuilds the same match engine    |
| Incompatible schemas                   | Each platform invents its own JSON (if any)                               | Integrations are brittle, require point-to-point ETL                            |
| Consent & privacy complexity           | Ad-hoc Terms of Service, email opt-ins, duplicative GDPR implementations  | Third parties can't reliably know if sharing data is legal                      |
| Cost of deep AI matching               | Every org builds embeddings or calls GPT independently                    | Redundant compute costs; small orgs get priced out                              |
| No canonical IDs                       | Email ≠ LinkedIn ≠ wallet ≠ Discord ≠ DID                                 | Cross-platform identity mapping is manual, fragmented, and error-prone          |

## What FA-API contributes

| Layer                   | Concrete Value-Add                                                                                     |
|-------------------------|--------------------------------------------------------------------------------------------------------|
| a. Ontology contract     | One directory of paths (e.g., `/alignment/job_recruitment/...`) so all apps describe needs/offers the same way. |
| b. Minimal REST schema   | Five endpoints anyone can implement in a weekend; guarantees you can always `GET /matches`.            |
| c. DID-centric IDs       | A self-sovereign identifier that already works in BlueSky, ActivityPub, Web5 — no more ad-hoc auth.    |
| d. Public-stream convention | Any server can ingest the public feed; everyone gets a free bootstrap graph.                       |
| e. Built-in consent flags | `public`, `consent` fields travel with the data — no more guessing GDPR basis.                        |
| f. Cost-layered matching  | Cheap and expensive linkers share the same endpoint; pay for depth only when needed — no duplication. |
| g. Plug-in graph adapters | Reference code for Arango/Neo4j/NetworkX removes boilerplate for newcomers.                           |


3 Is this “clever” or genuinely new?
Closest analogues
ActivityPub federates micro-blogs; Open Referral standardises human-services data; Schema.org offers loose JSON-LD hints.
None unify (a) business-grade consent, (b) multi-domain ontology, and (c) AI-ready match scoring in a single, minimal contract.

## Why now?

- DIDs are finally practical (AT Protocol, wallet DID methods).
- LLMs make semantic matching affordable, but only if data is portable.
- Regulators push data-portability and privacy by design.

## What makes it sustainable rather than novelty?

- It solves a daily integration pain for every consultant/marketplace.
- It doesn’t ask incumbents to rip out back-ends—just add one feed + five endpoints.
- Incentive-compatible: sharing public objects increases inbound matches; deeper AI can still be monetised via credits.

## 🎯 Deep-Dive: Minimal Universal Schema for AlignmentObjects

This section explains why a *single base layer* works across use-cases (jobs, grants, climate credits, DAO bounties), and what every AlignmentObject **must** contain.

---

### 🧩 1. Why a Base Layer Works

Think of every AlignmentObject like a **business card** — simple, scannable, and universal.

| Business-Card Analogy     | FA-API Field       | Purpose                                                   |
|---------------------------|--------------------|-----------------------------------------------------------|
| Company logo              | `actor_did`        | Who owns this object?                                     |
| Card type (“Engineer”)    | `path`             | Where it sits in the shared ontology tree                 |
| Tagline / bullet points   | `tags[]`           | Quick filters for matching                                |
| Contact QR code           | `public`, `consent`| Can this be rebroadcast/shared?                           |
| Phone number              | `links[]`          | Cached links to related entities                          |
| Headshot or label         | `label`            | Human-readable name (≤140 chars)                          |

Any vertical — job boards, coral reef credits, bounty boards — can publish base-layer compliant objects.

---

### 📦 2. Entity Schema (🚦 Required Fields)

| Field             | Required | Notes                                                                 |
|------------------|----------|-----------------------------------------------------------------------|
| `id`             | ✅       | UUID or vertex key                                                    |
| `actor_did`      | ✅       | Self-sovereign ID (DID) of the publishing Entity                      |
| `path`           | ✅       | Ontology leaf (e.g. `/alignment/job_recruitment/...`)                |
| `label`          | ✅       | Title/summary (e.g., "Senior Backend Engineer")                      |
| `tags[]`         | ✅       | 1–20 lowercase keywords, use shared vocab where possible              |
| `public`         | ✅       | Boolean: may this object be re-broadcast?                             |
| `consent`        | ✅       | `"explicit" | "implicit" | "absent"`                                 |
| `created_at`     | ✅       | ISO-8601 UTC timestamp                                                 |
| `alignment_vector` | 🟡    | Optional 768-float embedding                                           |
| `extra_meta_uri` | 🟡       | URI or CID for domain-specific details (JSON, PDF, markdown, etc.)   |
| `links[]`        | 🟡       | Cached edge IDs for performance                                       |

🔗 Longer descriptions belong in `extra_meta_uri`, not in the base graph.

---


# Glossary
- Entity          = Persistent actor (person, corporation, DAO, AI agent)
- AlignmentObject = Time-bounded need/offer published by an Entity
- Edge            = Relation between Entity ↔ AlignmentObject or Entity ↔ Entity
- DID             = Self-sovereign identifier (AT-Proto, DID:Key, etc.)
- public          = Boolean: may be re-broadcast / cached by any server
- consent         = explicit | implicit | absent     (GDPR art.6 mapping)
- path            = Ontology address  (/alignment/<vertical>/<...leaf>)
