import unittest
from stubs.mock_p2_engine import MockP2Engine
from person3_orchestration.orchestrator import CaseOrchestrator


class TestPerson3Orchestrator(unittest.TestCase):

    def setUp(self):
        self.mock_p2 = MockP2Engine()
        self.orchestrator = CaseOrchestrator(p1_repository=None, p2_engine=self.mock_p2)

    def test_completed_scenario(self):
        case = self.orchestrator.get_application_case("TEST-COMPLETED")
        self.assertEqual(case.state["normalized"], "COMPLETED")
        self.assertFalse(case.state["blocker"]["blocked"])
        self.assertIn("COMPLETED", case.jev_decision_assessment.summary)
        self.assertEqual(case.jev_decision_assessment.confidence_score, 1.0)

    def test_blocked_scenario(self):
        case = self.orchestrator.get_application_case("TEST-BLOCKED")
        self.assertEqual(case.state["normalized"], "BLOCKED")
        self.assertTrue(case.state["blocker"]["blocked"])
        self.assertEqual(case.state["blocker"]["organization"], "Payment Provider")
        self.assertEqual(case.state["next_owner"]["organization"], "Payment Operations")
        self.assertEqual(case.jev_decision_assessment.confidence_score, 0.4)

    def test_processing_scenario(self):
        case = self.orchestrator.get_application_case("TEST-PROCESSING")
        self.assertEqual(case.state["normalized"], "PROCESSING_NORMALLY")
        self.assertFalse(case.state["blocker"]["blocked"])
        self.assertEqual(case.jev_decision_assessment.confidence_score, 1.0)

    def test_unresolved_scenario(self):
        case = self.orchestrator.get_application_case("TEST-UNRESOLVED")
        self.assertEqual(case.reconciliation["status"], "UNRESOLVED")
        self.assertTrue(case.reconciliation["review_required"])
        self.assertIsNotNone(case.jev_decision_assessment.uncertainty_note)
        self.assertEqual(case.jev_decision_assessment.confidence_score, 0.2)

    def test_evaluate_person2_refund_case(self):
        from datetime import datetime, timedelta
        from core.models.input_evidence import EvidenceRecord, SourceOrganization
        from core.pipeline import create_refund_case

        t0 = datetime(2026, 10, 1, 10, 0)
        records = [
            EvidenceRecord(source_organization=SourceOrganization.BOOKING_PLATFORM, source_record_id="BK-1", source_status="REFUND_REQUESTED", passenger="John Doe", booking_ref="BK123", refund_amount=250.0, timestamp=t0),
            EvidenceRecord(source_organization=SourceOrganization.AIRLINE, source_record_id="AIR-1", source_status="REFUND_AUTHORIZED", passenger="John Doe", booking_ref="BK123", refund_amount=250.0, timestamp=t0 + timedelta(minutes=30)),
        ]
        p2_case = create_refund_case(records)
        case = self.orchestrator.evaluate_refund_case(p2_case)
        self.assertEqual(case.reconciliation["status"], "MATCHED")
        self.assertIsNotNone(case.jev_decision_assessment.confidence_score)
        self.assertGreater(case.jev_decision_assessment.confidence_score, 0.0)


if __name__ == "__main__":
    unittest.main()
