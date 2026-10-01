from src.sources.booking import BookingRecord
from src.adapters.evidence import EvidenceRecord


def adapt_booking(record: BookingRecord) -> EvidenceRecord:
    return EvidenceRecord(
        source_organization="booking_platform",
        source_record_id=record.booking_id,
        source_status=record.status,

        customer_passenger={
            "name": record.passenger_name
        },

        booking_information={
            "booking_id": record.booking_id
        },

        flight_information={
            "flight_number": record.flight_number
        },

        flight_date=record.flight_date,

        refund_amount=record.amount,

        transaction_information={
            "refund_id": record.refund_id
        },

        timestamp=record.timestamp,

        other_source_attributes={}
    )