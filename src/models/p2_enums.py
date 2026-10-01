from enum import Enum


class ReconciliationStatus(str, Enum):
    MATCHED = "MATCHED"
    DISCREPANCY = "DISCREPANCY"
    UNRESOLVED = "UNRESOLVED"


class NormalizedState(str, Enum):
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"
    PROCESSING_NORMALLY = "PROCESSING_NORMALLY"
    UNRESOLVED = "UNRESOLVED"
