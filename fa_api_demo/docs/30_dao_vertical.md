# Federated Alignment main branch as a DAO
Treat the Federated Alignment API itself as a DAO, and publish a vertical app dedicated to DAO-to-DAO alignment; Sam + Birger run the first instance, but any group can fork it, join the alignment graph, and earn on-chain governance power by contributing code or ontology upgrades.

Facet | Existing World | What DAO-Alignment Vertical Adds
DAO tooling | Proposal & vote tools are platform-siloed (Snapshot, Tally, Governor). | Canonical, cross-chain ontology for alignment objects (governance proposals, merge requests, funding pledges) so DAOs can inter-operate.
Contributor rewards | Bounties live off-chain or in Discord. | Alignment objects encode “contribution intent” → discoverable by any AI agent.
Protocol evolution | Specs evolve in e-mails and GitHub PRs. | Ontology leaf /alignment/dao_governance/proposal stores every RFC in machine-readable form; votes become graph edges.


# Early versions of FA-API 
The Graph has four entities:
- Four entities (Sam, Birger, Sam-AI, Birger-AI).

It supports naive private DMs:
- Private DM channel using /alignment/direct_message/text

To “turn this into a DAO vertical” we need an alignment object that represents:
Sam ↔ Birger      = co-founders of the FA-API DAO
Sam-AI ↔ Birger-AI = agents that automate inbox polling, create proposals, tally votes

# How do we encode FA-API as an alignment object in the graph?

## 3.1 Alternative A — Governance Proposal Model
path        : /alignment/dao_governance/proposal
title       : "Create FA-API DAO and seed repo permissions"
actor_did   : did:plc:sam_human
tags        : ["governance","founders","repo"]
public      : true
consent     : none
body        : "Proposal: Sam & Birger become multisig owners of the master branch…"
links       : ["did:plc:birger_human"]      # edge type = recipient

## 3.2 Alternative B — Project Alignment Model
path        : /alignment/meta/project_alignment
title       : "Initial Maintainer Pact – FA-API"
actor_did   : did:plc:sam_human
tags        : ["maintainer","pact"]
public      : true
consent     : none
data        : {
  "repo"  : "github.com/fa-api/spec",
  "rights": ["commit","merge"],
  "threshold": 2              # N-of-M signatures
}
links       : ["did:plc:birger_human"]       # needs Birger's "signature" AlignmentObject

Pick A if you want DAO-native voting flows.
Pick B if you want a generic agreement object across many verticals.
For the founding agreement we recommend Alternative A (Governance Proposal), because it plugs directly into on-chain or Snapshot voting if you add those adapters later.


# DAO Voting in Demo TODO
Gap | Task | Who owns
DAO leaf paths | Add /alignment/dao_governance/proposal, /vote_yes, /vote_no. | Ontology PR
Vote edge types | Accept relation:"votes_for" & "votes_against". | main.py update
LLM template | Prompt that turns free-text idea → dao_governance/proposal JSON. | LLM prompt engineer
BlueSky watcher | Poll AT-Proto for public:true governance objects; sync to local graph. | Ingestor script
Signature flow | Birger-AI auto-creates vote_yes AlignmentObject when proposal ID found. | AI-agent code
UI | Web page listing proposals + vote counts. | Future vertical app