from typing import Any
from src.models.application_case import JevDecisionAssessment
from src.models.refund_case import RefundCase


class HallucinationGuardrailError(Exception):
    pass


class GuardrailsValidator:
    """Verifies that Jev's output adheres strictly to Person 2's deterministic reality."""

    @staticmethod
    def validate(assessment: JevDecisionAssessment, refund_case: Any) -> None:
        # Check 1: Ensure blocked cases reflect accurate blocker context
        if refund_case.blocker.blocked:
            blocker_org = (refund_case.blocker.organization or "").lower()
            if blocker_org and blocker_org not in assessment.decision_rationale.lower() and blocker_org not in assessment.summary.lower():
                raise HallucinationGuardrailError(
                    f"Jev failed to reference the deterministic blocker organization ({refund_case.blocker.organization}) in reasoning."
                )

        # Check 2: Unresolved cases must explicitly highlight uncertainty/human review
        if refund_case.review_required:
            if not assessment.uncertainty_note:
                raise HallucinationGuardrailError(
                    "Jev must provide an explicit uncertainty_note when review_required is True."
                )
