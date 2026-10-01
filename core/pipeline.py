import uuid
from typing import List
from core.engines.blocker import identify_blocker
from core.engines.normalizer import normalize_status
from core.engines.owner import determine_next_owner
from core.engines.reconciler import reconcile_records
from core.engines.state_machine import determine_state
from core.engines.timeline import build_timeline
from core.engines.timing import evaluate_timing
from core.models.input_evidence import EvidenceRecord
from core.models.internal_state import NormalizedState
from core.models.refund_case import RefundCase


def create_refund_case(records: List[EvidenceRecord]) -> RefundCase:
    """Main deterministic business logic pipeline converting EvidenceRecord[] into a single RefundCase."""

    # 1. Reconcile evidence
    reconciliation = reconcile_records(records)

    # Extract available entity data from primary record
    primary_rec = records[0] if records else None

    customer_info = {"name": primary_rec.customer_name} if primary_rec and primary_rec.customer_name else {}
    booking_info = {"booking_ref": primary_rec.booking_ref} if primary_rec and primary_rec.booking_ref else {}
    flight_info = {
        "flight_number": primary_rec.flight_number,
        "flight_date": primary_rec.flight_date
    } if primary_rec else {}

    refund_amount = next((r.refund_amount for r in records if r.refund_amount is not None), None)

    # Handle UNRESOLVED match early
    if reconciliation.status.value == "UNRESOLVED":
        return RefundCase(
            case_id=f"CASE-{uuid.uuid4().hex[:8].upper()}",
            customer=customer_info,
            booking=booking_info,
            flight=flight_info,
            refund_amount=refund_amount,
            source_records=records,
            reconciliation=reconciliation,
            normalized_state=NormalizedState.UNRESOLVED,
            timeline=[],
            blocker=identify_blocker(NormalizedState.UNRESOLVED, [], evaluate_timing([], records), records),
            next_owner=determine_next_owner(NormalizedState.UNRESOLVED, identify_blocker(NormalizedState.UNRESOLVED, [], evaluate_timing([], records), records)),
            review_required=True
        )

    # 2. Normalize Statuses
    _ = normalize_status(records)

    # 3. Build Timeline
    timeline = build_timeline(records)

    # 4. Evaluate Timing SLAs
    timing_eval = evaluate_timing(timeline, records)

    # 5. Determine State
    state = determine_state(reconciliation.status, timeline, timing_eval, records)

    # 6. Identify Blocker
    blocker = identify_blocker(state, timeline, timing_eval, records)

    # 7. Determine Next Owner
    owner = determine_next_owner(state, blocker)

    # Review required for BLOCKED, UNRESOLVED, or CONFLICTING cases
    review_required = state in (
        NormalizedState.BLOCKED,
        NormalizedState.UNRESOLVED,
        NormalizedState.CONFLICTING
    )

    # 8. Return RefundCase
    return RefundCase(
        case_id=f"CASE-{uuid.uuid4().hex[:8].upper()}",
        customer=customer_info,
        booking=booking_info,
        flight=flight_info,
        refund_amount=refund_amount,
        source_records=records,
        reconciliation=reconciliation,
        normalized_state=state,
        timeline=timeline,
        blocker=blocker,
        next_owner=owner,
        review_required=review_required
    )