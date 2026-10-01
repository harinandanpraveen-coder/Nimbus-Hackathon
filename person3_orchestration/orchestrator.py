import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional

# Ensure repository root is on sys.path for direct script execution
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from src.models.application_case import ApplicationReadyCase, CaseMetadata
from src.models.refund_case import RefundCase
from person3_orchestration.context_builder import ContextBuilder
from person3_orchestration.jev_engine import JevDecisionEngine


class CaseOrchestrator:
    """Main Orchestrator Entry Point for Person 3."""

    def __init__(self, p1_repository: Any = None, p2_engine: Any = None, jev_engine: Optional[JevDecisionEngine] = None):
        self.p1_repository = p1_repository
        self.p2_engine = p2_engine
        self.jev_engine = jev_engine or JevDecisionEngine()

    def evaluate_refund_case(self, refund_case: Any) -> ApplicationReadyCase:
        """
        Connects the output of Person 2's pipeline (or any RefundCase)
        directly into Jev Engine and assembles the ApplicationReadyCase.
        """
        # Step 1: Extract facts payload for Jev
        facts_payload = ContextBuilder.build_facts_payload(refund_case)

        # Step 2: Run Jev Decision Engine
        jev_assessment = self.jev_engine.evaluate_case(facts_payload, refund_case)

        # Step 3: Extract reconciliation details and confidence score
        rec = refund_case.reconciliation
        status_val = rec.status.value if hasattr(rec.status, "value") else str(rec.status)
        confidence_score = getattr(rec, "confidence_score", None)
        confidence_reason = getattr(rec, "confidence_reason", None)
        if not confidence_reason and hasattr(rec, "match_reasons"):
            confidence_reason = "; ".join(rec.match_reasons) if rec.match_reasons else "Reconciliation complete"

        state_val = (
            refund_case.normalized_state.value
            if hasattr(refund_case.normalized_state, "value")
            else str(refund_case.normalized_state)
        )

        def to_dict(obj):
            if hasattr(obj, "model_dump"):
                return obj.model_dump()
            if hasattr(obj, "dict"):
                return obj.dict()
            return dict(obj)

        timeline_list = [to_dict(event) for event in refund_case.timeline]

        # Step 4: Assemble final ApplicationReadyCase
        return ApplicationReadyCase(
            meta=CaseMetadata(case_id=refund_case.case_id, generated_at=datetime.now(timezone.utc)),
            reconciliation={
                "status": status_val,
                "confidence_score": confidence_score,
                "reason": confidence_reason,
                "review_required": refund_case.review_required,
            },
            state={
                "normalized": state_val,
                "blocker": to_dict(refund_case.blocker),
                "next_owner": to_dict(refund_case.next_owner),
            },
            timeline=timeline_list,
            evidence=getattr(refund_case, "source_records", []),
            jev_decision_assessment=jev_assessment,
            raw_refund_case=refund_case,
        )

    def get_application_case(self, case_id: str) -> ApplicationReadyCase:
        # Step 1: Retrieve deterministic RefundCase from Person 2
        refund_case = self.p2_engine.get_reconciled_case(case_id)
        return self.evaluate_refund_case(refund_case)


if __name__ == "__main__":
    from core.integration import run_integration
    from core.pipeline import create_refund_case
    from core.models.input_evidence import EvidenceRecord, SourceOrganization
    from datetime import timedelta

    print("=== Step 1: Running Person 1 + 2 Integration Pipeline ===")
    try:
        refund_case = run_integration()
    except RuntimeError as err:
        print(f"[Note] Live API servers (ports 8001-8003) offline: {err}")
        print("Falling back to simulated cross-organizational evidence...")
        t0 = datetime.now()
        sample_records = [
            EvidenceRecord(
                source_organization=SourceOrganization.BOOKING_PLATFORM,
                source_record_id="BK-9901",
                source_status="REFUND_REQUESTED",
                passenger="John Doe",
                booking_ref="BK123",
                flight="AI101",
                flight_date="2026-10-01",
                refund_amount=250.00,
                timestamp=t0
            ),
            EvidenceRecord(
                source_organization=SourceOrganization.AIRLINE,
                source_record_id="AIR-9281",
                source_status="REFUND_AUTHORIZED",
                passenger="John Doe",
                booking_ref="BK123",
                flight="AI101",
                flight_date="2026-10-01",
                refund_amount=250.00,
                timestamp=t0 + timedelta(minutes=30)
            ),
            EvidenceRecord(
                source_organization=SourceOrganization.PAYMENT_PROVIDER,
                source_record_id="PAY-1122",
                source_status="REFUND_INITIATED",
                passenger="John Doe",
                booking_ref="BK123",
                refund_amount=250.00,
                timestamp=t0 + timedelta(days=3)
            )
        ]
        refund_case = create_refund_case(sample_records)

    print("\n=== Step 2: Passing Output into CaseOrchestrator & Jev Engine ===")
    orchestrator = CaseOrchestrator()
    app_ready_case = orchestrator.evaluate_refund_case(refund_case)

    print("\n=== Step 3: Resulting ApplicationReadyCase (with Jev Score) ===")
    print(app_ready_case.model_dump_json(indent=2))
