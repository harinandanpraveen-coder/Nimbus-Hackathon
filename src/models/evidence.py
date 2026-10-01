from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel


class EvidenceRecord(BaseModel):
    """Standardized record model from Person 1 (Ingestion)."""

    source_organization: str  # Booking Platform, Airline, Payment Provider, Issuing Bank
    source_record_id: str
    original_status: str
    timestamp: datetime
    customer_id: Optional[str] = None
    passenger_name: Optional[str] = None
    booking_reference: Optional[str] = None
    flight_number: Optional[str] = None
    amount: Optional[float] = None
    raw_payload: Dict[str, Any] = {}
