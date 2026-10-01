from typing import Any, Dict
from src.models.refund_case import RefundCase


class ContextBuilder:
    """Converts Person 2's deterministic RefundCase into an immutable facts payload for Jev."""

    @staticmethod
    def build_facts_payload(refund_case: Any) -> Dict[str, Any]:
        rec = refund_case.reconciliation
        status_val = rec.status.value if hasattr(rec.status, "value") else str(rec.status)
        confidence_score = getattr(rec, "confidence_score", None)
        confidence_reason = getattr(rec, "confidence_reason", None)
        if not confidence_reason and hasattr(rec, "match_reasons"):
            confidence_reason = "; ".join(rec.match_reasons) if rec.match_reasons else "Deterministic reconciliation match"

        state_val = (
            refund_case.normalized_state.value
            if hasattr(refund_case.normalized_state, "value")
            else str(refund_case.normalized_state)
        )

        timeline_events = []
        for event in refund_case.timeline:
            ts = event.timestamp
            ts_str = ts.isoformat() if hasattr(ts, "isoformat") else str(ts)
            timeline_events.append({
                "source": event.source_organization,
                "event": event.event,
                "status": event.source_status,
                "timestamp": ts_str,
            })

        return {
            "case_id": refund_case.case_id,
            "reconciliation_status": status_val,
            "confidence_score": confidence_score,
            "reconciliation_reason": confidence_reason,
            "normalized_state": state_val,
            "refund_amount": float(refund_case.refund_amount) if refund_case.refund_amount is not None else None,
            "customer": refund_case.customer,
            "booking": refund_case.booking,
            "flight": refund_case.flight,
            "blocker": {
                "is_blocked": refund_case.blocker.blocked,
                "organization": refund_case.blocker.organization,
                "reason": refund_case.blocker.reason,
                "evidence_keys": refund_case.blocker.evidence,
            },
            "next_owner": {
                "organization": refund_case.next_owner.organization,
                "reason": refund_case.next_owner.reason,
            },
            "timeline": timeline_events,
            "review_required": refund_case.review_required,
        }
