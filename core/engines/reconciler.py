from typing import List, Tuple
from core.models.input_evidence import EvidenceRecord
from core.models.internal_state import ReconciliationStatus
from core.models.refund_case import ReconciliationResult


def _clean_str(val: str | None) -> str | None:
    return val.strip().upper() if val else None


def evaluate_record_pair(rec1: EvidenceRecord, rec2: EvidenceRecord) -> Tuple[float, List[str]]:
    """Evaluates similarity between two records based on key deterministic attributes."""
    score = 0.0
    reasons = []

    # 1. Direct identifiers (Booking Ref or Transaction ID)
    if rec1.booking_ref and rec2.booking_ref:
        if _clean_str(rec1.booking_ref) == _clean_str(rec2.booking_ref):
            score += 0.4
            reasons.append(f"Matching booking_ref: {rec1.booking_ref}")
        else:
            return 0.0, ["Conflicting booking_ref"]

    if rec1.transaction_id and rec2.transaction_id:
        if _clean_str(rec1.transaction_id) == _clean_str(rec2.transaction_id):
            score += 0.3
            reasons.append(f"Matching transaction_id: {rec1.transaction_id}")

    # 2. Passenger / Customer Name
    if rec1.customer_name and rec2.customer_name:
        if _clean_str(rec1.customer_name) == _clean_str(rec2.customer_name):
            score += 0.2
            reasons.append(f"Matching customer_name: {rec1.customer_name}")
        else:
            reasons.append("Mismatch in customer_name")

    # 3. Flight Info & Date
    if rec1.flight_number and rec2.flight_number:
        if _clean_str(rec1.flight_number) == _clean_str(rec2.flight_number):
            score += 0.15
            reasons.append(f"Matching flight_number: {rec1.flight_number}")

    if rec1.flight_date and rec2.flight_date:
        if rec1.flight_date == rec2.flight_date:
            score += 0.15
            reasons.append(f"Matching flight_date: {rec1.flight_date}")

    # 4. Refund Amount
    if rec1.refund_amount is not None and rec2.refund_amount is not None:
        if abs(rec1.refund_amount - rec2.refund_amount) < 0.01:
            score += 0.2
            reasons.append(f"Matching refund_amount: {rec1.refund_amount}")
        else:
            reasons.append(f"Mismatch refund_amount ({rec1.refund_amount} vs {rec2.refund_amount})")

    return score, reasons


def reconcile_records(records: List[EvidenceRecord]) -> ReconciliationResult:
    """Reconciles a list of EvidenceRecord objects into a unified match result."""
    if not records:
        return ReconciliationResult(
            status=ReconciliationStatus.UNRESOLVED,
            confidence_score=0.0,
            matched_record_ids=[],
            match_reasons=["No input evidence records provided."]
        )

    if len(records) == 1:
        return ReconciliationResult(
            status=ReconciliationStatus.MATCHED,
            confidence_score=1.0,
            matched_record_ids=[records[0].source_record_id],
            match_reasons=["Single evidence record provided."]
        )

    matched_ids = [r.source_record_id for r in records]
    accumulated_reasons = []
    scores = []

    # Pairwise matching across all records
    for i in range(len(records)):
        for j in range(i + 1, len(records)):
            score, pair_reasons = evaluate_record_pair(records[i], records[j])
            scores.append(score)
            accumulated_reasons.extend(pair_reasons)

    avg_score = sum(scores) / len(scores) if scores else 0.0

    # Decision threshold: Minimum score required to claim MATCHED
    if avg_score >= 0.45:
        return ReconciliationResult(
            status=ReconciliationStatus.MATCHED,
            confidence_score=round(min(avg_score, 1.0), 2),
            matched_record_ids=matched_ids,
            match_reasons=list(set(accumulated_reasons))
        )
    else:
        return ReconciliationResult(
            status=ReconciliationStatus.UNRESOLVED,
            confidence_score=round(avg_score, 2),
            matched_record_ids=[],
            match_reasons=list(set(accumulated_reasons)) + ["Insufficient cumulative matching evidence."]
        )