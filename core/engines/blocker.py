from typing import List
from core.models.input_evidence import EvidenceRecord
from core.models.internal_state import (
    BlockerDetails,
    NormalizedState,
    TimelineEvent,
    TimingEvaluation,
)


def identify_blocker(
    state: NormalizedState,
    timeline: List[TimelineEvent],
    timing_eval: TimingEvaluation,
    records: List[EvidenceRecord]
) -> BlockerDetails:
    """Identifies the blocking entity and evidence when a case is in a BLOCKED state."""

    # Unblocked states return empty details
    if state != NormalizedState.BLOCKED:
        return BlockerDetails(blocked=False, organization=None, reason=None, evidence=[])

    if not timeline:
        return BlockerDetails(
            blocked=True,
            organization="Unknown",
            reason="No event timeline available for blocked case.",
            evidence=[]
        )

    last_event = timeline[-1]
    last_org = last_event.source_organization

    # Determine missing downstream party based on last known stage
    downstream_map = {
        "Booking Platform": "Airline",
        "Airline": "Payment Provider",
        "Payment Provider": "Issuing Bank",
        "Issuing Bank": "Issuing Bank"
    }

    target_org = downstream_map.get(last_org, last_org)

    # Check for explicit rejection/failure events first
    failure_event = next((e for e in timeline if "FAILED" in e.event or "REJECTED" in e.event), None)
    if failure_event:
        return BlockerDetails(
            blocked=True,
            organization=failure_event.source_organization,
            reason=f"Explicit failure recorded: {failure_event.source_status}",
            evidence=[
                f"Source Record Status: {failure_event.source_status}",
                f"Timestamp: {failure_event.timestamp.isoformat()}"
            ]
        )

    # Timing window exceeded blocker
    evidence_items = [
        f"Last observed stage: {last_org} ({last_event.source_status})",
        f"Elapsed time: {timing_eval.elapsed_minutes} minutes",
        f"Expected SLA window: {timing_eval.expected_window_minutes} minutes"
    ]

    return BlockerDetails(
        blocked=True,
        organization=target_org,
        reason=f"Expected downstream transaction from {target_org} not observed within SLA window.",
        evidence=evidence_items
    )