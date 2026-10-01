from typing import List
from core.models.input_evidence import EvidenceRecord
from core.models.internal_state import (
    NormalizedState,
    ReconciliationStatus,
    TimelineEvent,
    TimingEvaluation,
    TimingStatus,
)


def determine_state(
    reconciliation_status: ReconciliationStatus,
    timeline: List[TimelineEvent],
    timing_eval: TimingEvaluation,
    records: List[EvidenceRecord]
) -> NormalizedState:
    """Main deterministic state machine governing the refund lifecycle state."""

    # Rule 1: Insufficient matching evidence
    if reconciliation_status == ReconciliationStatus.UNRESOLVED:
        return NormalizedState.UNRESOLVED

    # Rule 2: Conflicting core attributes (e.g., conflicting booking/transaction reference)
    if any("Conflicting" in reason for reason in getattr(records, "match_reasons", [])):
        return NormalizedState.CONFLICTING

    # Extract all normalized events present in the timeline
    events = [ev.event for ev in timeline]

    # Rule 3: Process Fully Completed (Bank credited or payment settled)
    if "TRANSACTION_CREDITED" in events or "REFUND_COMPLETED" in events:
        return NormalizedState.COMPLETED

    # Rule 4: Explicit Failure / Rejection
    if "REFUND_REJECTED" in events or "REFUND_FAILED" in events:
        return NormalizedState.BLOCKED

    # Rule 5: Timing SLA Exceeded without downstream completion
    if timing_eval.timing_status == TimingStatus.WINDOW_EXCEEDED:
        return NormalizedState.BLOCKED

    # Rule 6: Normal Active Processing within SLA Window
    if timing_eval.timing_status in (
        TimingStatus.WITHIN_EXPECTED_WINDOW,
        TimingStatus.NOT_APPLICABLE,
    ):
        return NormalizedState.PROCESSING_NORMALLY

    return NormalizedState.UNRESOLVED