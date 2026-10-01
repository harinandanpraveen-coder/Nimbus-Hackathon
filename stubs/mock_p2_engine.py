from datetime import datetime
from typing import Dict, Any

from src.models.refund_case import (
    RefundCase,
    ReconciliationResult,
    TimelineEvent,
    BlockerDetails,
    OwnerRecommendation,
)

from src.models.p2_enums import (
    ReconciliationStatus,
    NormalizedState,
)



class MockP2Engine:
    """Mock implementation of Person 2 Reconciliation Engine for testing Person 3."""

    def get_reconciled_case(self, case_id: str) -> RefundCase:
        if case_id == "TEST-COMPLETED":
            return RefundCase(
                case_id="TEST-COMPLETED",
                customer={"name": "John Doe", "email": "john@example.com"},
                booking={"pnr": "BK-9921", "status": "CANCELLED"},
                flight={"flight_no": "AI-101", "date": "2026-10-01"},
                refund_amount=250.0,
                source_records=[],
                reconciliation=ReconciliationResult(
                    status=ReconciliationStatus.MATCHED,
                    confidence_reason="All records match accurately across all 4 sources.",
                ),
                normalized_state=NormalizedState.COMPLETED,
                timeline=[
                    TimelineEvent(
                        source_organization="Booking Platform",
                        event="Cancellation requested",
                        source_status="CANCELLED",
                        timestamp=datetime(2026, 10, 1, 10, 0),
                    ),
                    TimelineEvent(
                        source_organization="Airline",
                        event="Refund authorized",
                        source_status="AUTHORIZED",
                        timestamp=datetime(2026, 10, 1, 10, 15),
                    ),
                    TimelineEvent(
                        source_organization="Payment Provider",
                        event="Refund processed",
                        source_status="COMPLETED",
                        timestamp=datetime(2026, 10, 1, 11, 0),
                    ),
                    TimelineEvent(
                        source_organization="Issuing Bank",
                        event="Credit posted",
                        source_status="CREDITED",
                        timestamp=datetime(2026, 10, 1, 12, 0),
                    ),
                ],
                blocker=BlockerDetails(blocked=False),
                next_owner=OwnerRecommendation(
                    organization="None", reason="Case completed successfully"
                ),
                review_required=False,
            )

        elif case_id == "TEST-BLOCKED":
            return RefundCase(
                case_id="TEST-BLOCKED",
                customer={"name": "Alice Smith", "email": "alice@example.com"},
                booking={"pnr": "BK-1102", "status": "CANCELLED"},
                flight={"flight_no": "BA-202", "date": "2026-10-01"},
                refund_amount=450.0,
                source_records=[],
                reconciliation=ReconciliationResult(
                    status=ReconciliationStatus.MATCHED,
                    confidence_reason="Matching records identified across Airline and Payment Provider.",
                ),
                normalized_state=NormalizedState.BLOCKED,
                timeline=[
                    TimelineEvent(
                        source_organization="Airline",
                        event="Refund authorized",
                        source_status="AUTHORIZED",
                        timestamp=datetime(2026, 10, 1, 10, 0),
                    ),
                    TimelineEvent(
                        source_organization="Payment Provider",
                        event="Batch processing started",
                        source_status="PROCESSING",
                        timestamp=datetime(2026, 10, 1, 10, 15),
                    ),
                ],
                blocker=BlockerDetails(
                    blocked=True,
                    organization="Payment Provider",
                    reason="Downstream settlement transaction not observed within 24h SLA window",
                    evidence=["PAY-PROC-9912"],
                ),
                next_owner=OwnerRecommendation(
                    organization="Payment Operations",
                    reason="Trace stuck batch transaction at payment gateway",
                ),
                review_required=False,
            )

        elif case_id == "TEST-PROCESSING":
            return RefundCase(
                case_id="TEST-PROCESSING",
                customer={"name": "Bob Lee", "email": "bob@example.com"},
                booking={"pnr": "BK-3301", "status": "CANCELLED"},
                flight={"flight_no": "UA-303", "date": "2026-10-02"},
                refund_amount=180.0,
                source_records=[],
                reconciliation=ReconciliationResult(
                    status=ReconciliationStatus.MATCHED,
                    confidence_reason="Records matched; clearing window active.",
                ),
                normalized_state=NormalizedState.PROCESSING_NORMALLY,
                timeline=[
                    TimelineEvent(
                        source_organization="Airline",
                        event="Refund authorized",
                        source_status="AUTHORIZED",
                        timestamp=datetime(2026, 10, 2, 2, 0),
                    ),
                ],
                blocker=BlockerDetails(blocked=False),
                next_owner=OwnerRecommendation(
                    organization="Automated System",
                    reason="Awaiting standard clearing cycle",
                ),
                review_required=False,
            )

        else:  # TEST-UNRESOLVED
            return RefundCase(
                case_id="TEST-UNRESOLVED",
                customer={"name": "Unknown", "email": "unknown@example.com"},
                booking={"pnr": "BK-0000", "status": "UNKNOWN"},
                flight={"flight_no": "XX-000", "date": "2026-10-01"},
                refund_amount=300.0,
                source_records=[],
                reconciliation=ReconciliationResult(
                    status=ReconciliationStatus.UNRESOLVED,
                    confidence_reason="Discrepancy in passenger names and amounts across sources.",
                ),
                normalized_state=NormalizedState.UNRESOLVED,
                timeline=[],
                blocker=BlockerDetails(blocked=False),
                next_owner=OwnerRecommendation(
                    organization="Manual Operations Desk",
                    reason="Reconcile conflicting metadata records",
                ),
                review_required=True,
            )
