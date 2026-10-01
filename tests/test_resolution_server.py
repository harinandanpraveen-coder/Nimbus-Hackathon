import os
import sys
import unittest

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from resolution_api_server import (
    run_test_scenario,
    run_pipeline_for_booking,
    run_custom_records
)


class TestResolutionServerEndpoints(unittest.TestCase):

    def test_scenario_a_completed(self):
        case = run_test_scenario("A")
        self.assertEqual(case.state["normalized"], "COMPLETED")
        self.assertFalse(case.state["blocker"]["blocked"])
        self.assertEqual(case.reconciliation["status"], "MATCHED")

    def test_scenario_b_blocked(self):
        case = run_test_scenario("B")
        self.assertEqual(case.state["normalized"], "BLOCKED")
        self.assertTrue(case.state["blocker"]["blocked"])
        self.assertIn("Bank", case.state["blocker"]["organization"])

    def test_scenario_c_processing(self):
        case = run_test_scenario("C")
        self.assertEqual(case.state["normalized"], "PROCESSING_NORMALLY")
        self.assertFalse(case.state["blocker"]["blocked"])

    def test_scenario_d_unresolved(self):
        case = run_test_scenario("D")
        self.assertEqual(case.state["normalized"], "UNRESOLVED")
        self.assertTrue(case.reconciliation["review_required"])

    def test_live_pipeline_for_bk_20006(self):
        case = run_pipeline_for_booking("BK-20006")
        self.assertEqual(case.state["normalized"], "BLOCKED")
        self.assertTrue(case.state["blocker"]["blocked"])
        self.assertEqual(case.state["blocker"]["organization"], "Payment Provider")
        self.assertEqual(case.jev_decision_assessment.escalation_priority, "HIGH")

    def test_custom_records_resolution(self):
        custom_records = [
            {
                "source_organization": "Booking Platform",
                "source_record_id": "BK-TEST",
                "booking_ref": "BK-100",
                "passenger": "Test Passenger",
                "flight": "AI-101",
                "refund_amount": 500.0,
                "source_status": "REFUND_REQUESTED"
            },
            {
                "source_organization": "Airline",
                "source_record_id": "AIR-TEST",
                "booking_ref": "BK-100",
                "passenger": "Test Passenger",
                "flight": "AI-101",
                "refund_amount": 500.0,
                "source_status": "REFUND_AUTHORIZED"
            }
        ]
        case = run_custom_records(custom_records)
        self.assertEqual(case.reconciliation["status"], "MATCHED")
        self.assertIsNotNone(case.meta.case_id)


if __name__ == "__main__":
    unittest.main()
