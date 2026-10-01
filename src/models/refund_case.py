from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from src.models.p2_enums import ReconciliationStatus, NormalizedState
from src.models.evidence import EvidenceRecord


class TimelineEvent(BaseModel):
    source_organization: str
    event: str
    source_status: str
    timestamp: datetime


class ReconciliationResult(BaseModel):
    status: ReconciliationStatus
    confidence_reason: str


class BlockerDetails(BaseModel):
    blocked: bool = False
    organization: Optional[str] = "None"
    reason: Optional[str] = "No blocker identified"
    evidence: List[str] = Field(default_factory=list)


class OwnerRecommendation(BaseModel):
    organization: str
    reason: str


class RefundCase(BaseModel):
    case_id: str
    customer: Dict[str, Any]
    booking: Dict[str, Any]
    flight: Dict[str, Any]
    refund_amount: float
    source_records: List[EvidenceRecord] = Field(default_factory=list)
    reconciliation: ReconciliationResult
    normalized_state: NormalizedState
    timeline: List[TimelineEvent] = Field(default_factory=list)
    blocker: BlockerDetails
    next_owner: OwnerRecommendation
    review_required: bool = False
