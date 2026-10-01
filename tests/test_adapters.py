import unittest

from src.adapters.booking_adapter import adapt_booking
from src.adapters.airline_adapter import adapt_airline
from src.adapters.payment_adapter import adapt_payment

from src.data.mock_data import (
    MOCK_BOOKING_RECORDS,
    MOCK_AIRLINE_RECORDS,
    MOCK_PAYMENT_RECORDS,
)


class TestEvidenceAdapters(unittest.TestCase):

    def test_booking_adapter(self):
        evidence = adapt_booking(MOCK_BOOKING_RECORDS[0])
        data = evidence.to_dict()

        self.assertEqual(data["source_organization"], "booking_platform")
        self.assertEqual(data["source_record_id"], "BOOK-A001")
        self.assertEqual(data["source_status"], "REFUND_COMPLETED")
        self.assertEqual(data["customer_passenger"]["name"], "Rahul Sharma")
        self.assertEqual(data["booking_information"]["booking_id"], "BOOK-A001")
        self.assertEqual(data["flight_information"]["flight_number"], "AI-101")
        self.assertEqual(data["flight_date"], "2026-10-15")
        self.assertEqual(data["refund_amount"], 12500.0)
        self.assertEqual(
            data["transaction_information"]["refund_id"],
            "REF-A001",
        )


    def test_airline_adapter(self):
        evidence = adapt_airline(MOCK_AIRLINE_RECORDS[0])
        data = evidence.to_dict()

        self.assertEqual(data["source_organization"], "airline")
        self.assertEqual(data["source_record_id"], "AIR-REF-A001")
        self.assertEqual(data["source_status"], "REFUNDED")
        self.assertEqual(data["customer_passenger"]["name"], "Rahul Sharma")
        self.assertEqual(data["booking_information"], {})
        self.assertEqual(data["flight_information"]["flight_number"], "AI-101")
        self.assertEqual(data["flight_date"], "2026-10-15")
        self.assertEqual(data["refund_amount"], 12500.0)
        self.assertEqual(
            data["transaction_information"]["airline_refund_id"],
            "AIR-REF-A001",
        )


    def test_payment_adapter(self):
        evidence = adapt_payment(MOCK_PAYMENT_RECORDS[0])
        data = evidence.to_dict()

        self.assertEqual(data["source_organization"], "payment_provider")
        self.assertEqual(data["source_record_id"], "TXN-A001")
        self.assertEqual(data["source_status"], "SETTLED")
        self.assertEqual(data["customer_passenger"], {})
        self.assertEqual(data["booking_information"], {})
        self.assertEqual(data["flight_information"], {})
        self.assertIsNone(data["flight_date"])
        self.assertEqual(data["refund_amount"], 12500.0)
        self.assertEqual(
            data["transaction_information"]["transaction_id"],
            "TXN-A001",
        )
        self.assertEqual(
            data["transaction_information"]["refund_reference"],
            "REF-A001",
        )


    def test_common_evidence_structure(self):
        evidence_records = [
            adapt_booking(MOCK_BOOKING_RECORDS[0]),
            adapt_airline(MOCK_AIRLINE_RECORDS[0]),
            adapt_payment(MOCK_PAYMENT_RECORDS[0]),
        ]

        expected_fields = {
            "source_organization",
            "source_record_id",
            "source_status",
            "customer_passenger",
            "booking_information",
            "flight_information",
            "flight_date",
            "refund_amount",
            "transaction_information",
            "timestamp",
            "other_source_attributes",
        }

        for evidence in evidence_records:
            data = evidence.to_dict()

            self.assertEqual(
                set(data.keys()),
                expected_fields,
            )


if __name__ == "__main__":
    unittest.main()