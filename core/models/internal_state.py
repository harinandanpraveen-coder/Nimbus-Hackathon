from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel


class ReconciliationStatus(str, Enum):
    MATCHED = "MATCHED"
    UNRESOLVED = "UNRESOLVED"


class NormalizedState(str, Enum):
    PROCESSING_NORMALLY = "PROCESSING_NORMALLY"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"
    CONFLICTING = "CONFLICTING"
    UNRESOLVED = "UNRESOLVED"


class TimingStatus(str, Enum):
    WITHIN_EXPECTED_WINDOW = "WITHIN_EXPECTED_WINDOW"
    WINDOW_EXCEEDED = "WINDOW_EXCEEDED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class TimelineEvent(BaseModel):
    source_organization: str
    event: str
    source_status: str
    timestamp: datetime


class TimingEvaluation(BaseModel):
    timing_status: TimingStatus
    elapsed_minutes: Optional[float] = None
    expected_window_minutes: Optional[float] = None


class BlockerDetails(BaseModel):
    blocked: bool
    organization: Optional[str] = None
    reason: Optional[str] = None
    evidence: List[str] = []


class OwnerRecommendation(BaseModel):
    organization: str
    reason: str