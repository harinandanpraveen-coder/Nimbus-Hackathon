from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class PaymentRecord:
    """
    Record received from the Payment Provider.

    The payment provider has its own transaction/refund identifiers
    and its own status terminology.
    """

    transaction_id: str
    refund_reference: str

    amount: Decimal

    status: str
    timestamp: datetime