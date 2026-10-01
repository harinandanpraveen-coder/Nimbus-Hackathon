import unittest
from datetime import datetime
from decimal import Decimal

from src.sources.booking import BookingRecord
from src.sources.airline import AirlineRecord
from src.sources.payment import PaymentRecord

from src.data.mock_data import (
    MOCK_BOOKING_RECORDS,
    MOCK_AIRLINE_RECORDS,
    MOCK_PAYMENT_RECORDS,
)


class TestSourceRecords(unittest.TestCase):

    def test_booking_record(self):
        record = BookingRecord(
            booking_id="BOOK-001",
            passenger_name="John Doe",
            flight_number="AI-101",
            flight_date="2026-10-15",
            refund_id="REF-001",
            amount=Decimal("12500.00"),
            status="REFUND_REQUESTED",
            timestamp=datetime(2026, 10, 1, 10, 30),
        )

        self.assertEqual(record.booking_id, "BOOK-001")
        self.assertEqual(record.status, "REFUND_REQUESTED")
        self.assertEqual(record.amount, Decimal("12500.00"))

    def test_airline_record(self):
        record = AirlineRecord(
            airline_refund_id="AIR-REF-001",
            passenger_name="John Doe",
            flight_number="AI-101",
            flight_date="2026-10-15",
            amount=Decimal("12500.00"),
            status="AUTHORIZED",
            timestamp=datetime(2026, 10, 1, 11, 0),
        )

        self.assertEqual(record.airline_refund_id, "AIR-REF-001")
        self.assertEqual(record.status, "AUTHORIZED")

    def test_payment_record(self):
        record = PaymentRecord(
            transaction_id="TXN-001",
            refund_reference="REF-001",
            amount=Decimal("12500.00"),
            status="PROCESSING",
            timestamp=datetime(2026, 10, 1, 12, 0),
        )

        self.assertEqual(record.transaction_id, "TXN-001")
        self.assertEqual(record.status, "PROCESSING")

    def test_mock_data(self):
        self.assertEqual(len(MOCK_BOOKING_RECORDS), 4)
        self.assertEqual(len(MOCK_AIRLINE_RECORDS), 4)
        self.assertEqual(len(MOCK_PAYMENT_RECORDS), 4)

        self.assertEqual(
            MOCK_BOOKING_RECORDS[0].status,
            "REFUND_COMPLETED"
        )

        self.assertEqual(
            MOCK_AIRLINE_RECORDS[1].status,
            "ON_HOLD"
        )

        self.assertEqual(
            MOCK_PAYMENT_RECORDS[2].status,
            "PROCESSING"
        )

        self.assertEqual(
            MOCK_BOOKING_RECORDS[3].refund_id,
            "REF-D001"
        )


if __name__ == "__main__":
    unittest.main()