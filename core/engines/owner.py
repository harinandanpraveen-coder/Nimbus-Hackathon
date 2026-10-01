from core.models.internal_state import BlockerDetails, NormalizedState, OwnerRecommendation


def determine_next_owner(
    state: NormalizedState,
    blocker: BlockerDetails
) -> OwnerRecommendation:
    """Determines which operational entity owns the next investigation step."""

    # Standard completion
    if state == NormalizedState.COMPLETED:
        return OwnerRecommendation(
            organization="System / None",
            reason="Refund process successfully completed."
        )

    # Normal processing in progress
    if state == NormalizedState.PROCESSING_NORMALLY:
        return OwnerRecommendation(
            organization="System Automated Tracking",
            reason="Case is progressing normally within operational SLA bounds."
        )

    # Unresolved or conflicting matches need human review
    if state in (NormalizedState.UNRESOLVED, NormalizedState.CONFLICTING):
        return OwnerRecommendation(
            organization="Human Review",
            reason="Insufficient or conflicting evidence across source records requires manual reconciliation."
        )

    # Blocked state owner routing
    if state == NormalizedState.BLOCKED and blocker.organization:
        org_owner_map = {
            "Booking Platform": "Booking Operations",
            "Airline": "Airline Operations",
            "Payment Provider": "Payment Operations",
            "Issuing Bank": "Bank/Settlement Operations"
        }

        owner_team = org_owner_map.get(blocker.organization, "Human Review")
        return OwnerRecommendation(
            organization=owner_team,
            reason=blocker.reason or f"Action required by {owner_team} to resolve issue."
        )

    return OwnerRecommendation(
        organization="Human Review",
        reason="Case state requires manual intervention."
    )