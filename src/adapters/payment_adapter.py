from src.sources.payment import PaymentRecord
from src.adapters.evidence import EvidenceRecord


def adapt_payment(record: PaymentRecord) -> EvidenceRecord:
    return EvidenceRecord(
        source_organization="payment_provider",
        source_record_id=record.transaction_id,
        source_status=record.status,

        customer_passenger={},

        booking_information={},

        flight_information={},

        flight_date=None,

        refund_amount=record.amount,

        transaction_information={
            "transaction_id": record.transaction_id,
            "refund_reference": record.refund_reference
        },

        timestamp=record.timestamp,

        other_source_attributes={}
    )