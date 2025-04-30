from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# ───────────────────────────────────────── Relation enum
class Relation(str, Enum):
    author_of     = "author_of"
    controls      = "controls"
    context_push  = "context_push"   # broadcast result
    recipient     = "recipient"      # DM
    interested_in = "interested_in"  # acceptance / reply


# ───────────────────────────────────────── Core models
class EntityIn(BaseModel):
    did: str
    label: str
    type: str  # Human | AI | Org
    subscriptions: Optional[List[str]] = []
    controls: Optional[str] = None


class AlignmentObjectIn(BaseModel):
    path: str
    actor_did: str
    label: str
    tags: List[str] = Field(default_factory=list)
    public: bool = False
    consent: str = "explicit"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    # Optional DM fields
    target_did: Optional[str] = None
    body: Optional[str] = None


class EdgeIn(BaseModel):
    _from: str
    _to: str
    relation: Relation