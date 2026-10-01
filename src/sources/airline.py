from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class AirlineRecord:
    """
    Record received from the Airline system.

    The airline has its own identifiers and status terminology.
    """

    airline_refund_id: str
    passenger_name: str

    flight_number: str
    flight_date: str

    amount: Decimal

    status: str
    timestamp: datetime