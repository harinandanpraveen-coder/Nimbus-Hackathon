from datetime import datetime, timedelta
from core.models.input_evidence import EvidenceRecord, SourceOrganization
from core.models.internal_state import NormalizedState
from core.pipeline import create_refund_case


def test_scenario_a_completed():
    """Scenario A — Completed Refund"""
    t0 = datetime(2026, 10, 1, 10, 0)
    records = [
        EvidenceRecord(source_organization=SourceOrganization.BOOKING_PLATFORM, source_record_id="BK-1", source_status="REFUND_REQUESTED", passenger="John Doe", booking_ref="BK123", refund_amount=250.0, timestamp=t0),
        EvidenceRecord(source_organization=SourceOrganization.AIRLINE, source_record_id="AIR-1", source_status="REFUND_AUTHORIZED", passenger="John Doe", booking_ref="BK123", refund_amount=250.0, timestamp=t0 + timedelta(minutes=30)),
        EvidenceRecord(source_organization=SourceOrganization.PAYMENT_PROVIDER, source_record_id="PAY-1", source_status="COMPLETED", passenger="John Doe", booking_ref="BK123", refund_amount=250.0, timestamp=t0 + timedelta(hours=2)),
        EvidenceRecord(source_organization=SourceOrganization.ISSUING_BANK, source_record_id="BNK-1", source_status="CREDITED", passenger="John Doe", booking_ref="BK123", refund_amount=250.0, timestamp=t0 + timedelta(hours=5))
    ]
    case = create_refund_case(records)
    assert case.normalized_state == NormalizedState.COMPLETED
    assert case.blocker.blocked is False


def test_scenario_b_blocked():
    """Scenario B — Blocked Refund (SLA Exceeded)"""
    t0 = datetime(2026, 10, 1, 10, 0)
    records = [
        EvidenceRecord(source_organization=SourceOrganization.BOOKING_PLATFORM, source_record_id="BK-2", source_status="REFUND_REQUESTED", passenger="Jane Smith", booking_ref="BK456", refund_amount=180.0, timestamp=t0),
        EvidenceRecord(source_organization=SourceOrganization.AIRLINE, source_record_id="AIR-2", source_status="REFUND_AUTHORIZED", passenger="Jane Smith", booking_ref="BK456", refund_amount=180.0, timestamp=t0 + timedelta(minutes=30)),
        EvidenceRecord(source_organization=SourceOrganization.PAYMENT_PROVIDER, source_record_id="PAY-2", source_status="REFUND_INITIATED", passenger="Jane Smith", booking_ref="BK456", refund_amount=180.0, timestamp=t0 + timedelta(days=3))
    ]
    case = create_refund_case(records)
    assert case.normalized_state == NormalizedState.BLOCKED
    assert case.blocker.blocked is True
    assert case.next_owner.organization == "Bank/Settlement Operations"


def test_scenario_c_normal_processing():
    """Scenario C — Normal Processing within SLA"""
    t0 = datetime(2026, 10, 1, 10, 0)
    records = [
        EvidenceRecord(source_organization=SourceOrganization.AIRLINE, source_record_id="AIR-3", source_status="REFUND_AUTHORIZED", passenger="Alice N", booking_ref="BK789", refund_amount=300.0, timestamp=t0),
        EvidenceRecord(source_organization=SourceOrganization.PAYMENT_PROVIDER, source_record_id="PAY-3", source_status="PROCESSING", passenger="Alice N", booking_ref="BK789", refund_amount=300.0, timestamp=t0 + timedelta(minutes=15))
    ]
    case = create_refund_case(records)
    assert case.normalized_state == NormalizedState.PROCESSING_NORMALLY
    assert case.blocker.blocked is False


def test_scenario_d_unresolved():
    """Scenario D — Unresolved Match (Insufficient Evidence)"""
    t0 = datetime(2026, 10, 1, 10, 0)
    records = [
        EvidenceRecord(source_organization=SourceOrganization.BOOKING_PLATFORM, source_record_id="BK-4", source_status="REFUND_REQUESTED", passenger="Bob Wright", booking_ref="BK999", refund_amount=500.0, timestamp=t0),
        EvidenceRecord(source_organization=SourceOrganization.AIRLINE, source_record_id="AIR-4", source_status="REFUND_AUTHORIZED", passenger="Charlie Brown", booking_ref="BK000", refund_amount=100.0, timestamp=t0)
    ]
    case = create_refund_case(records)
    assert case.normalized_state == NormalizedState.UNRESOLVED
    assert case.review_required is True