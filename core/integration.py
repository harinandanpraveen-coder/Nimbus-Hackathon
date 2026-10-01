
"""
Integration Entry Point

Connects the source APIs to Person 1's adapters
and Person 2's reconciliation pipeline.

Existing source files remain untouched.
"""

import json
from datetime import datetime
from decimal import Decimal
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

# Source models
from src.sources.booking import BookingRecord
from src.sources.airline import AirlineRecord
from src.sources.payment import PaymentRecord

# Person 1's adapters
from src.adapters.booking_adapter import adapt_booking
from src.adapters.airline_adapter import adapt_airline
from src.adapters.payment_adapter import adapt_payment

# Person 2's pipeline model and function
from core.models.input_evidence import (
    EvidenceRecord as PipelineEvidenceRecord
)
from core.pipeline import create_refund_case


# API base URLs
BOOKING_API_URL = "http://127.0.0.1:8001"
AIRLINE_API_URL = "http://127.0.0.1:8002"
PAYMENT_API_URL = "http://127.0.0.1:8003"


# --------------------------------------------------
# STEP 1: FETCH DATA FROM ALL THREE APIS
# --------------------------------------------------

def fetch_json(url):
    """Fetch JSON data from an API endpoint."""

    try:
        with urlopen(url, timeout=10) as response:
            return json.loads(
                response.read().decode("utf-8")
            )

    except (URLError, HTTPError) as error:
        raise RuntimeError(
            f"Could not retrieve data from {url}: {error}"
        ) from error


def fetch_booking_data():
    url = f"{BOOKING_API_URL}/api/booking/bookings"
    return fetch_json(url)["bookings"]


def fetch_airline_data():
    url = f"{AIRLINE_API_URL}/api/airline/tickets"
    return fetch_json(url)["tickets"]


def fetch_payment_data():
    url = f"{PAYMENT_API_URL}/api/payment/transactions"
    return fetch_json(url)["transactions"]


def fetch_payment_detail(payment_ref):
    """Fetch detailed payment data using API 6."""

    url = (
        f"{PAYMENT_API_URL}/api/payment/transactions/"
        f"{payment_ref}"
    )

    return fetch_json(url)


# --------------------------------------------------
# STEP 2: CONVERT API RESPONSES INTO SOURCE MODELS
# --------------------------------------------------

def parse_timestamp(value):
    return datetime.strptime(
        value,
        "%Y-%m-%d %H:%M"
    )


def convert_to_booking_record(raw):
    """Convert API JSON into Person 1's BookingRecord."""

    return BookingRecord(
        booking_id=raw["bookingRef"],
        passenger_name=raw["customer"],
        flight_number=raw["flightNo"],
        flight_date=raw["flightDate"],
        refund_id=raw["refundId"],
        amount=Decimal(str(raw["amount"])),
        status=raw["status"],
        timestamp=parse_timestamp(raw["bookedAt"])
    )


def convert_to_airline_record(raw):
    """Convert API JSON into Person 1's AirlineRecord."""

    departure = parse_timestamp(raw["departure"])

    return AirlineRecord(
        airline_refund_id=raw["pnr"],
        passenger_name=raw["passenger"],
        flight_number=raw["flightNo"],
        flight_date=departure.date().isoformat(),
        amount=Decimal(str(raw["fare"])),
        status=raw["status"],
        timestamp=departure
    )


def convert_to_payment_record(raw, detail):
    """Convert API JSON into Person 1's PaymentRecord."""

    return PaymentRecord(
        transaction_id=detail.get(
            "gatewayTxnId",
            raw["paymentRef"]
        ),
        refund_reference=raw["paymentRef"],
        amount=Decimal(str(raw["amount"])),
        status=raw["status"],
        timestamp=parse_timestamp(raw["paidAt"])
    )


# --------------------------------------------------
# STEP 3: CONVERT PERSON 1 OUTPUT TO PERSON 2 INPUT
# --------------------------------------------------

def convert_to_pipeline_record(record, source_name):
    """
    Convert Person 1's EvidenceRecord dataclass into
    Person 2's Pydantic EvidenceRecord.
    """

    source_organizations = {
        "booking": "Booking Platform",
        "airline": "Airline",
        "payment": "Payment Provider"
    }

    organization = source_organizations[source_name]

    customer_info = record.customer_passenger or {}
    booking_info = record.booking_information or {}
    flight_info = record.flight_information or {}
    transaction_info = record.transaction_information or {}

    refund_amount = record.refund_amount

    transaction_id = (
        transaction_info.get("transaction_id")
        or transaction_info.get("refund_id")
        or transaction_info.get("airline_refund_id")
        or transaction_info.get("refund_reference")
    )

    return PipelineEvidenceRecord(
        source_organization=organization,

        source_record_id=record.source_record_id,
        source_status=record.source_status,

        customer_name=customer_info.get("name"),

        booking_ref=booking_info.get("booking_id"),

        flight_number=flight_info.get("flight_number"),

        flight_date=record.flight_date,

        refund_amount=(
            float(refund_amount)
            if refund_amount is not None
            else None
        ),

        transaction_id=transaction_id,

        timestamp=record.timestamp,

        other_source_attributes=(
            record.other_source_attributes or {}
        )
    )


# --------------------------------------------------
# STEP 4: MAIN INTEGRATION PIPELINE
# --------------------------------------------------

def run_integration():

    print("Starting Fork0ff integration...")

    # Fetch raw records from all three APIs
    print("\nFetching Booking records...")
    raw_bookings = fetch_booking_data()

    print("Fetching Airline records...")
    raw_airline = fetch_airline_data()

    print("Fetching Payment records...")
    raw_payments = fetch_payment_data()

    print(
        f"\nFetched {len(raw_bookings)} booking records, "
        f"{len(raw_airline)} airline records, "
        f"and {len(raw_payments)} payment records."
    )

    # Convert raw JSON into source-specific models
    booking_inputs = [
        convert_to_booking_record(raw)
        for raw in raw_bookings
    ]

    airline_inputs = [
        convert_to_airline_record(raw)
        for raw in raw_airline
    ]

    payment_inputs = []

    for raw in raw_payments:
        detail = fetch_payment_detail(
            raw["paymentRef"]
        )

        payment_inputs.append(
            convert_to_payment_record(raw, detail)
        )

    # Run Person 1's adapters
    print("\nRunning source adapters...")

    booking_outputs = [
        adapt_booking(record)
        for record in booking_inputs
    ]

    airline_outputs = [
        adapt_airline(record)
        for record in airline_inputs
    ]

    payment_outputs = [
        adapt_payment(record)
        for record in payment_inputs
    ]

    # Preserve booking references for cross-source matching.
    # The existing airline and payment adapters leave these blank.
    for evidence, raw in zip(
        airline_outputs, raw_airline
    ):
        evidence.booking_information["booking_id"] = (
            raw["bookingRef"]
        )

    for evidence, raw in zip(
        payment_outputs, raw_payments
    ):
        evidence.booking_information["booking_id"] = (
            raw["bookingRef"]
        )

    # Convert all adapter outputs into Person 2's model
    print("Converting evidence into pipeline format...")

    pipeline_records = []

    pipeline_records.extend(
        convert_to_pipeline_record(record, "booking")
        for record in booking_outputs
    )

    pipeline_records.extend(
        convert_to_pipeline_record(record, "airline")
        for record in airline_outputs
    )

    pipeline_records.extend(
        convert_to_pipeline_record(record, "payment")
        for record in payment_outputs
    )

    print(
        f"Prepared {len(pipeline_records)} evidence records."
    )

    # Pass combined evidence to Person 2's pipeline
    print("\nRunning reconciliation pipeline...")

    refund_case = create_refund_case(
        pipeline_records
    )

    return refund_case


# --------------------------------------------------
# ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":

    result = run_integration()

    print("\nIntegration completed successfully!")

    if hasattr(result, "model_dump_json"):
        print(result.model_dump_json(indent=2))
    else:
        print(result)
