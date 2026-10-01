from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from src.models.evidence import EvidenceRecord
from src.models.refund_case import RefundCase


class CaseMetadata(BaseModel):
    case_id: str
    generated_at: datetime


class JevDecisionAssessment(BaseModel):
    summary: str
    decision_rationale: str
    recommended_action: str
    escalation_priority: str
    confidence_score: Optional[float] = 1.0
    uncertainty_note: Optional[str] = None


class ApplicationReadyCase(BaseModel):
    meta: CaseMetadata
    reconciliation: Dict[str, Any]
    state: Dict[str, Any]
    timeline: List[Dict[str, Any]]
    evidence: List[Any]
    jev_decision_assessment: JevDecisionAssessment
    raw_refund_case: Any


# Aliases for flexibility
ApplicationCase = ApplicationReadyCase
