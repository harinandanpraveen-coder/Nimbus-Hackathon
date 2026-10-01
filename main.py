import json
from datetime import datetime, timedelta
from core.models.input_evidence import EvidenceRecord, SourceOrganization
from core.pipeline import create_refund_case


def main():
    # 1. Simulate incoming evidence records from Person 1
    t0 = datetime(2026, 10, 1, 10, 0)

    sample_evidence_records = [
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
            timestamp=t0 + timedelta(days=3)  # Intentionally exceeds SLA window
        )
    ]

    print("--- Executing Person 2 Engine ---")

    # 2. Process records into RefundCase
    refund_case = create_refund_case(sample_evidence_records)

    # 3. Output the RefundCase as structured JSON (Contract for Person 3)
    case_json = refund_case.model_dump_json(indent=2)
    print(case_json)


if __name__ == "__main__":
    main()