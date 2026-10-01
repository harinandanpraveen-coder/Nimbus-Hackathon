from src.models.application_case import JevDecisionAssessment
from src.models.refund_case import RefundCase


class FallbackGenerator:
    """Template-based deterministic fallback generator when Jev API is unavailable or fails validation."""

    @staticmethod
    def generate_fallback(refund_case: Any) -> JevDecisionAssessment:
        base_score = getattr(refund_case.reconciliation, "confidence_score", None)
        if base_score is None:
            base_score = 1.0

        if refund_case.blocker.blocked:
            summary = f"Refund case {refund_case.case_id} is BLOCKED at {refund_case.blocker.organization}."
            rationale = refund_case.blocker.reason or "Blocked due to process exception or timing SLA breach."
            action = f"Escalate to {refund_case.next_owner.organization}: {refund_case.next_owner.reason}"
            priority = "HIGH"
            computed_score = round(float(base_score) * 0.4, 2)
        elif refund_case.review_required:
            summary = f"Refund case {refund_case.case_id} is UNRESOLVED and requires human review."
            rec_reason = getattr(refund_case.reconciliation, "confidence_reason", None)
            if not rec_reason and hasattr(refund_case.reconciliation, "match_reasons"):
                rec_reason = "; ".join(refund_case.reconciliation.match_reasons)
            rationale = rec_reason or "Manual review required due to record discrepancies."
            action = f"Route to {refund_case.next_owner.organization} for manual reconciliation."
            priority = "HIGH"
            computed_score = round(float(base_score) * 0.2, 2)
        else:
            state_val = (
                refund_case.normalized_state.value
                if hasattr(refund_case.normalized_state, "value")
                else str(refund_case.normalized_state)
            )
            summary = f"Refund case {refund_case.case_id} state is {state_val}."
            rationale = "All processing steps are proceeding according to standard operations."
            action = "No immediate manual intervention required."
            priority = "LOW"
            computed_score = round(float(base_score), 2)

        return JevDecisionAssessment(
            summary=summary,
            decision_rationale=rationale,
            recommended_action=action,
            escalation_priority=priority,
            confidence_score=computed_score,
            uncertainty_note="Manual review required due to record discrepancies." if refund_case.review_required else None,
        )
