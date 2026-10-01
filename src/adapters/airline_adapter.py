from src.sources.airline import AirlineRecord
from src.adapters.evidence import EvidenceRecord


def adapt_airline(record: AirlineRecord) -> EvidenceRecord:
    return EvidenceRecord(
        source_organization="airline",
        source_record_id=record.airline_refund_id,
        source_status=record.status,

        customer_passenger={
            "name": record.passenger_name
        },

        booking_information={},

        flight_information={
            "flight_number": record.flight_number
        },

        flight_date=record.flight_date,

        refund_amount=record.amount,

        transaction_information={
            "airline_refund_id": record.airline_refund_id
        },

        timestamp=record.timestamp,

        other_source_attributes={}
    )