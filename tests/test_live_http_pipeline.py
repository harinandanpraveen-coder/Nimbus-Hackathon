import os
import sys
import pytest

# Ensure repository root is on sys.path
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from core.integration import (
    BOOKING_API_URL,
    AIRLINE_API_URL,
    PAYMENT_API_URL,
    fetch_booking_data,
    fetch_airline_data,
    fetch_payment_data,
    fetch_payment_detail,
    convert_to_booking_record,
    convert_to_airline_record,
    convert_to_payment_record,
    adapt_booking,
    adapt_airline,
    adapt_payment,
    convert_to_pipeline_record,
    run_integration,
)
from core.pipeline import create_refund_case
from person3_orchestration.orchestrator import CaseOrchestrator


def test_live_http_endpoints_reachable():
    """Verify that all 3 microservices are responding to live HTTP requests."""
    bookings = fetch_booking_data()
    tickets = fetch_airline_data()
    payments = fetch_payment_data()

    assert len(bookings) > 0, "No bookings returned from Booking API"
    assert len(tickets) > 0, "No tickets returned from Airline API"
    assert len(payments) > 0, "No transactions returned from Payment API"


def test_live_http_single_booking_pipeline():
    """Verify end-to-end flow for a specific live booking (e.g. BK-20006 - FAILED payment)."""
    raw_bookings = fetch_booking_data()
    raw_airline = fetch_airline_data()
    raw_payments = fetch_payment_data()

    bk_ref = "BK-20006"
    b_raw = [r for r in raw_bookings if r.get("bookingRef") == bk_ref]
    a_raw = [r for r in raw_airline if r.get("bookingRef") == bk_ref]
    p_raw = [r for r in raw_payments if r.get("bookingRef") == bk_ref]

    assert len(b_raw) == 1
    assert len(a_raw) == 1
    assert len(p_raw) == 1

    b_recs = [convert_to_pipeline_record(adapt_booking(convert_to_booking_record(r)), "booking") for r in b_raw]
    a_recs = []
    for r in a_raw:
        ad = adapt_airline(convert_to_airline_record(r))
        ad.booking_information["booking_id"] = r["bookingRef"]
        a_recs.append(convert_to_pipeline_record(ad, "airline"))
    p_recs = []
    for r in p_raw:
        dt = fetch_payment_detail(r["paymentRef"])
        ad = adapt_payment(convert_to_payment_record(r, dt))
        ad.booking_information["booking_id"] = r["bookingRef"]
        p_recs.append(convert_to_pipeline_record(ad, "payment"))

    # Person 2 pipeline
    refund_case = create_refund_case(b_recs + a_recs + p_recs)

    # Person 3 Orchestration + Jev Engine
    orchestrator = CaseOrchestrator()
    app_case = orchestrator.evaluate_refund_case(refund_case)

    # Assertions on live outputs
    assert app_case.meta.case_id == refund_case.case_id
    assert app_case.reconciliation["status"] == "MATCHED"
    assert app_case.reconciliation["confidence_score"] > 0.7
    assert app_case.state["normalized"] == "BLOCKED"
    assert app_case.jev_decision_assessment.escalation_priority == "HIGH"
    assert "FAILED" in app_case.jev_decision_assessment.recommended_action


def test_live_http_full_integration_pipeline():
    """Verify Person 1 + 2 run_integration() with live HTTP data directly feeds Person 3."""
    refund_case = run_integration()
    orchestrator = CaseOrchestrator()
    app_case = orchestrator.evaluate_refund_case(refund_case)

    assert app_case is not None
    assert app_case.jev_decision_assessment is not None
    assert app_case.reconciliation["confidence_score"] is not None


if __name__ == "__main__":
    print("=" * 80)
    print("LIVE HTTP END-TO-END PIPELINE DEMONSTRATION")
    print("=" * 80)

    print("\n[1] Pinging Live HTTP Endpoints:")
    bookings = fetch_booking_data()
    airline = fetch_airline_data()
    payments = fetch_payment_data()
    print(f"  --> Booking API ({BOOKING_API_URL}): {len(bookings)} bookings fetched")
    print(f"  --> Airline API ({AIRLINE_API_URL}): {len(airline)} airline tickets fetched")
    print(f"  --> Payment API ({PAYMENT_API_URL}): {len(payments)} transactions fetched")

    print("\n[2] Executing Full Pipeline on Booking BK-20006 (Live HTTP Input):")
    bk_ref = "BK-20006"
    b_raw = [r for r in bookings if r.get("bookingRef") == bk_ref]
    a_raw = [r for r in airline if r.get("bookingRef") == bk_ref]
    p_raw = [r for r in payments if r.get("bookingRef") == bk_ref]

    b_recs = [convert_to_pipeline_record(adapt_booking(convert_to_booking_record(r)), "booking") for r in b_raw]
    a_recs = []
    for r in a_raw:
        ad = adapt_airline(convert_to_airline_record(r))
        ad.booking_information["booking_id"] = r["bookingRef"]
        a_recs.append(convert_to_pipeline_record(ad, "airline"))
    p_recs = []
    for r in p_raw:
        dt = fetch_payment_detail(r["paymentRef"])
        ad = adapt_payment(convert_to_payment_record(r, dt))
        ad.booking_information["booking_id"] = r["bookingRef"]
        p_recs.append(convert_to_pipeline_record(ad, "payment"))

    refund_case = create_refund_case(b_recs + a_recs + p_recs)
    orchestrator = CaseOrchestrator()
    app_case = orchestrator.evaluate_refund_case(refund_case)

    print("\n--- PRODUCED OUTPUT (ApplicationReadyCase) ---")
    print(f"Case ID                 : {app_case.meta.case_id}")
    print(f"Generated At            : {app_case.meta.generated_at}")
    print(f"Normalized State        : {app_case.state['normalized']}")
    print(f"Blocker                 : {app_case.state['blocker']}")
    print(f"Next Owner              : {app_case.state['next_owner']}")
    print(f"Reconciliation Status   : {app_case.reconciliation['status']}")
    print(f"Reconciliation Score    : {app_case.reconciliation['confidence_score']}")
    print(f"Reconciliation Reason   : {app_case.reconciliation['reason']}")
    print(f"Jev Assessment Score    : {app_case.jev_decision_assessment.confidence_score}")
    print(f"Jev Escalation Priority : {app_case.jev_decision_assessment.escalation_priority}")
    print(f"Jev Recommended Action  : {app_case.jev_decision_assessment.recommended_action}")
    print(f"Jev Decision Summary    : {app_case.jev_decision_assessment.summary}")
    print("=" * 80)
