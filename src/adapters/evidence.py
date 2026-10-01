from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional


@dataclass
class EvidenceRecord:
    source_organization: str
    source_record_id: str
    source_status: str

    customer_passenger: Dict[str, Any]
    booking_information: Dict[str, Any]
    flight_information: Dict[str, Any]

    flight_date: Optional[str]

    refund_amount: Decimal

    transaction_information: Dict[str, Any]

    timestamp: datetime

    other_source_attributes: Dict[str, Any]

    def to_dict(self) -> dict:
        return {
            "source_organization": self.source_organization,
            "source_record_id": self.source_record_id,
            "source_status": self.source_status,
            "customer_passenger": self.customer_passenger,
            "booking_information": self.booking_information,
            "flight_information": self.flight_information,
            "flight_date": self.flight_date,
            "refund_amount": float(self.refund_amount),
            "transaction_information": self.transaction_information,
            "timestamp": self.timestamp.isoformat(),
            "other_source_attributes": self.other_source_attributes,
        }