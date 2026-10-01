from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


class SourceOrganization(str, Enum):
    BOOKING_PLATFORM = "Booking Platform"
    AIRLINE = "Airline"
    PAYMENT_PROVIDER = "Payment Provider"
    ISSUING_BANK = "Issuing Bank"


class EvidenceRecord(BaseModel):
    """Standardized evidence input provided by Person 1."""

    model_config = ConfigDict(populate_by_name=True)

    source_organization: SourceOrganization
    source_record_id: str
    source_status: str
    customer_name: Optional[str] = Field(default=None, alias="passenger")
    booking_ref: Optional[str] = None
    flight_number: Optional[str] = Field(default=None, alias="flight")
    flight_date: Optional[str] = None  # Format: YYYY-MM-DD
    refund_amount: Optional[float] = None
    transaction_id: Optional[str] = None
    timestamp: datetime
    other_source_attributes: Dict[str, Any] = Field(default_factory=dict)