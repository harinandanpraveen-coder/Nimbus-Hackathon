from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class BookingRecord:
    """
    Record received from the Booking Platform.

    This represents the source's original data.
    No normalization or reconciliation happens here.
    """

    booking_id: str
    passenger_name: str

    flight_number: str
    flight_date: str

    refund_id: str
    amount: Decimal

    status: str
    timestamp: datetime