from typing import Dict, Tuple

# Maps (source_organization, raw_source_status) -> normalized_status_string
STATUS_MAPPING: Dict[Tuple[str, str], str] = {
    # Booking Platform
    ("Booking Platform", "REFUND_REQUESTED"): "REFUND_REQUESTED",
    ("Booking Platform", "PENDING"): "REFUND_REQUESTED",
    ("Booking Platform", "CANCELLED"): "REFUND_REQUESTED",

    # Airline
    ("Airline", "REFUND_AUTHORIZED"): "REFUND_AUTHORIZED",
    ("Airline", "AUTHORIZED"): "REFUND_AUTHORIZED",
    ("Airline", "APPROVED"): "REFUND_AUTHORIZED",
    ("Airline", "REJECTED"): "REFUND_REJECTED",

    # Payment Provider
    ("Payment Provider", "REFUND_INITIATED"): "REFUND_INITIATED",
    ("Payment Provider", "PROCESSING"): "REFUND_INITIATED",
    ("Payment Provider", "SETTLED"): "REFUND_COMPLETED",
    ("Payment Provider", "COMPLETED"): "REFUND_COMPLETED",
    ("Payment Provider", "FAILED"): "REFUND_FAILED",

    # Issuing Bank
    ("Issuing Bank", "CREDITED"): "TRANSACTION_CREDITED",
    ("Issuing Bank", "SETTLED"): "TRANSACTION_CREDITED",
    ("Issuing Bank", "NO_TRANSACTION"): "NOT_RECEIVED",
    ("Issuing Bank", "PENDING"): "NOT_RECEIVED",
}