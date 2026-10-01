from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from .input_evidence import EvidenceRecord
from .internal_state import (
    BlockerDetails,
    NormalizedState,
    OwnerRecommendation,
    ReconciliationStatus,
    TimelineEvent,
)


class ReconciliationResult(BaseModel):
    status: ReconciliationStatus
    confidence_score: float
    matched_record_ids: List[str]
    match_reasons: List[str]


class RefundCase(BaseModel):
    """Final unified object generated for Person 3."""

    case_id: str
    customer: Dict[str, Any]
    booking: Dict[str, Any]
    flight: Dict[str, Any]
    refund_amount: Optional[float]
    source_records: List[EvidenceRecord]
    reconciliation: ReconciliationResult
    normalized_state: NormalizedState
    timeline: List[TimelineEvent]
    blocker: BlockerDetails
    next_owner: OwnerRecommendation
    review_required: bool