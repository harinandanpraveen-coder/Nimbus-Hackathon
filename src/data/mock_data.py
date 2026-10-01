from datetime import datetime
from decimal import Decimal

from src.sources.booking import BookingRecord
from src.sources.airline import AirlineRecord
from src.sources.payment import PaymentRecord


# ============================================================
# CASE A — COMPLETED REFUND
# ============================================================

CASE_A_BOOKING = BookingRecord(
    booking_id="BOOK-A001",
    passenger_name="Rahul Sharma",
    flight_number="AI-101",
    flight_date="2026-10-15",
    refund_id="REF-A001",
    amount=Decimal("12500.00"),
    status="REFUND_COMPLETED",
    timestamp=datetime(2026, 10, 1, 10, 0),
)

CASE_A_AIRLINE = AirlineRecord(
    airline_refund_id="AIR-REF-A001",
    passenger_name="Rahul Sharma",
    flight_number="AI-101",
    flight_date="2026-10-15",
    amount=Decimal("12500.00"),
    status="REFUNDED",
    timestamp=datetime(2026, 10, 2, 10, 0),
)

CASE_A_PAYMENT = PaymentRecord(
    transaction_id="TXN-A001",
    refund_reference="REF-A001",
    amount=Decimal("12500.00"),
    status="SETTLED",
    timestamp=datetime(2026, 10, 3, 10, 0),
)


# ============================================================
# CASE B — BLOCKED REFUND
# ============================================================

CASE_B_BOOKING = BookingRecord(
    booking_id="BOOK-B001",
    passenger_name="Priya Mehta",
    flight_number="6E-202",
    flight_date="2026-10-18",
    refund_id="REF-B001",
    amount=Decimal("8500.00"),
    status="REFUND_REQUESTED",
    timestamp=datetime(2026, 10, 1, 9, 0),
)

CASE_B_AIRLINE = AirlineRecord(
    airline_refund_id="AIR-REF-B001",
    passenger_name="Priya Mehta",
    flight_number="6E-202",
    flight_date="2026-10-18",
    amount=Decimal("8500.00"),
    status="ON_HOLD",
    timestamp=datetime(2026, 10, 2, 9, 0),
)

CASE_B_PAYMENT = PaymentRecord(
    transaction_id="TXN-B001",
    refund_reference="REF-B001",
    amount=Decimal("8500.00"),
    status="NOT_RECEIVED",
    timestamp=datetime(2026, 10, 3, 9, 0),
)


# ============================================================
# CASE C — NORMAL PROCESSING
# Different source statuses, but the events are progressing.
# ============================================================

CASE_C_BOOKING = BookingRecord(
    booking_id="BOOK-C001",
    passenger_name="Arjun Patel",
    flight_number="UK-303",
    flight_date="2026-10-20",
    refund_id="REF-C001",
    amount=Decimal("15000.00"),
    status="REFUND_REQUESTED",
    timestamp=datetime(2026, 10, 1, 8, 0),
)

CASE_C_AIRLINE = AirlineRecord(
    airline_refund_id="AIR-REF-C001",
    passenger_name="Arjun Patel",
    flight_number="UK-303",
    flight_date="2026-10-20",
    amount=Decimal("15000.00"),
    status="AUTHORIZED",
    timestamp=datetime(2026, 10, 2, 8, 0),
)

CASE_C_PAYMENT = PaymentRecord(
    transaction_id="TXN-C001",
    refund_reference="REF-C001",
    amount=Decimal("15000.00"),
    status="PROCESSING",
    timestamp=datetime(2026, 10, 3, 8, 0),
)


# ============================================================
# CASE D — UNRESOLVED MATCH
# ============================================================

CASE_D_BOOKING = BookingRecord(
    booking_id="BOOK-D001",
    passenger_name="Amit Kumar",
    flight_number="AI-404",
    flight_date="2026-10-22",
    refund_id="REF-D001",
    amount=Decimal("9200.00"),
    status="REFUND_REQUESTED",
    timestamp=datetime(2026, 10, 1, 7, 0),
)

CASE_D_AIRLINE = AirlineRecord(
    airline_refund_id="AIR-REF-D999",
    passenger_name="Unknown Passenger",
    flight_number="UNKNOWN",
    flight_date="2026-10-25",
    amount=Decimal("11000.00"),
    status="AUTHORIZED",
    timestamp=datetime(2026, 10, 2, 7, 0),
)

CASE_D_PAYMENT = PaymentRecord(
    transaction_id="TXN-D999",
    refund_reference="REF-D999",
    amount=Decimal("11000.00"),
    status="PROCESSING",
    timestamp=datetime(2026, 10, 3, 7, 0),
)


# ============================================================
# GROUP ALL MOCK DATA
# ============================================================

MOCK_BOOKING_RECORDS = [
    CASE_A_BOOKING,
    CASE_B_BOOKING,
    CASE_C_BOOKING,
    CASE_D_BOOKING,
]

MOCK_AIRLINE_RECORDS = [
    CASE_A_AIRLINE,
    CASE_B_AIRLINE,
    CASE_C_AIRLINE,
    CASE_D_AIRLINE,
]

MOCK_PAYMENT_RECORDS = [
    CASE_A_PAYMENT,
    CASE_B_PAYMENT,
    CASE_C_PAYMENT,
    CASE_D_PAYMENT,
]