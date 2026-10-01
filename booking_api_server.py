
import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs


HOST = "127.0.0.1"
PORT = 8001


# Demo source data based on the records in booking.html.
# flightDate and refundId are explicit placeholders because
# the original website data does not contain these fields.

BOOKINGS = [
    {
        "bookingRef": "BK-20001",
        "customer": "Aarav Sharma",
        "airlinePnr": "MR1001",
        "flightNo": "MR201",
        "origin": "CCU",
        "destination": "DEL",
        "amount": 5400,
        "paymentRef": "PAY-90001",
        "status": "CONFIRMED",
        "bookedAt": "2026-10-01 10:12",
        "flightDate": "2026-10-10",
        "refundId": "DEMO-REF-BK-20001",
        "currency": "INR",
        "email": "aarav@example.com"
    },
    {
        "bookingRef": "BK-20002",
        "customer": "Priya Das",
        "airlinePnr": "MR1002",
        "flightNo": "MR305",
        "origin": "CCU",
        "destination": "BOM",
        "amount": 6200,
        "paymentRef": "PAY-90002",
        "status": "CONFIRMED",
        "bookedAt": "2026-10-01 11:40",
        "flightDate": "2026-10-10",
        "refundId": "DEMO-REF-BK-20002",
        "currency": "INR",
        "email": "priya@example.com"
    },
    {
        "bookingRef": "BK-20003",
        "customer": "Rohan Mehta",
        "airlinePnr": "MR1003",
        "flightNo": "MR118",
        "origin": "DEL",
        "destination": "BLR",
        "amount": 7100,
        "paymentRef": "PAY-90003",
        "status": "CONFIRMED",
        "bookedAt": "2026-10-02 09:05",
        "flightDate": "2026-10-10",
        "refundId": "DEMO-REF-BK-20003",
        "currency": "INR",
        "email": "rohan@example.com"
    },
    {
        "bookingRef": "BK-20004",
        "customer": "Ananya Roy",
        "airlinePnr": "MR1004",
        "flightNo": "MR410",
        "origin": "BOM",
        "destination": "CCU",
        "amount": 5800,
        "paymentRef": "PAY-90004",
        "status": "CANCELLED",
        "bookedAt": "2026-10-02 14:30",
        "flightDate": "2026-10-10",
        "refundId": "DEMO-REF-BK-20004",
        "currency": "INR",
        "email": "ananya@example.com"
    },
    {
        "bookingRef": "BK-20005",
        "customer": "Vikram Singh",
        "airlinePnr": "MR1005",
        "flightNo": "MR222",
        "origin": "BLR",
        "destination": "HYD",
        "amount": 3200,
        "paymentRef": "PAY-90005",
        "status": "REFUND_INITIATED",
        "bookedAt": "2026-10-03 08:20",
        "flightDate": "2026-10-10",
        "refundId": "DEMO-REF-BK-20005",
        "currency": "INR",
        "email": "vikram@example.com"
    },
    {
        "bookingRef": "BK-20006",
        "customer": "Sneha Iyer",
        "airlinePnr": "MR1006",
        "flightNo": "MR201",
        "origin": "CCU",
        "destination": "DEL",
        "amount": 5400,
        "paymentRef": "PAY-90006",
        "status": "CONFIRMED",
        "bookedAt": "2026-10-03 16:45",
        "flightDate": "2026-10-10",
        "refundId": "DEMO-REF-BK-20006",
        "currency": "INR",
        "email": "sneha@example.com"
    },
    {
        "bookingRef": "BK-20007",
        "customer": "Kabir Khan",
        "airlinePnr": "MR1007",
        "flightNo": "MR509",
        "origin": "HYD",
        "destination": "CCU",
        "amount": 5100,
        "paymentRef": "PAY-90007",
        "status": "CONFIRMED",
        "bookedAt": "2026-10-04 12:00",
        "flightDate": "2026-10-10",
        "refundId": "DEMO-REF-BK-20007",
        "currency": "INR",
        "email": "kabir@example.com"
    },
    {
        "bookingRef": "BK-20008",
        "customer": "Meera Nair",
        "airlinePnr": "MR1008",
        "flightNo": "MR118",
        "origin": "DEL",
        "destination": "BLR",
        "amount": 7100,
        "paymentRef": "PAY-90008",
        "status": "CONFIRMED",
        "bookedAt": "2026-10-04 19:10",
        "flightDate": "2026-10-10",
        "refundId": "DEMO-REF-BK-20008",
        "currency": "INR",
        "email": "meera@example.com"
    },
    {
        "bookingRef": "BK-20009",
        "customer": "Rahul Verma",
        "airlinePnr": "MR1009",
        "flightNo": "MR201",
        "origin": "CCU",
        "destination": "DEL",
        "amount": 5400,
        "paymentRef": "PAY-90009",
        "status": "CONFIRMED",
        "bookedAt": "2026-10-05 07:55",
        "flightDate": "2026-10-10",
        "refundId": "DEMO-REF-BK-20009",
        "currency": "INR",
        "email": "rahul@example.com"
    }
]


class BookingAPIHandler(BaseHTTPRequestHandler):

    def send_json(self, status, data):
        body = json.dumps(data).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            data = json.loads(raw_body)
        except Exception:
            data = {}

        if path == "/api/booking/bookings":
            bref = str(data.get("bookingRef", "")).upper()
            existing = next((b for b in BOOKINGS if b["bookingRef"] == bref), None)
            if existing:
                existing.update(data)
                self.send_json(200, {"api": "API 1", "status": "updated", "booking": existing})
            else:
                if not bref:
                    bref = f"BK-{20000 + len(BOOKINGS) + 1}"
                    data["bookingRef"] = bref
                if "bookedAt" not in data:
                    data["bookedAt"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                if "flightDate" not in data:
                    data["flightDate"] = "2026-10-10"
                if "refundId" not in data:
                    data["refundId"] = f"DEMO-REF-{bref}"
                if "currency" not in data:
                    data["currency"] = "INR"
                BOOKINGS.append(data)
                self.send_json(201, {"api": "API 1", "status": "created", "booking": data})
            return

        prefix = "/api/booking/bookings/"
        if path.startswith(prefix):
            bref = path[len(prefix):].upper()
            existing = next((b for b in BOOKINGS if b["bookingRef"] == bref), None)
            if existing:
                existing.update(data)
                self.send_json(200, {"api": "API 2", "status": "updated", "booking": existing})
                return
            self.send_json(404, {"error": "Booking not found"})
            return

        self.send_json(404, {"error": "Unknown endpoint"})

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        # API 1: List bookings
        if path == "/api/booking/bookings":

            status_filter = params.get("status", [None])[0]

            results = [
                {
                    key: booking[key]
                    for key in (
                        "bookingRef",
                        "customer",
                        "airlinePnr",
                        "flightNo",
                        "origin",
                        "destination",
                        "amount",
                        "paymentRef",
                        "status",
                        "bookedAt",
                        "flightDate",
                        "refundId"
                    )
                }
                for booking in BOOKINGS
                if not status_filter
                or booking["status"] == status_filter.upper()
            ]

            self.send_json(200, {
                "api": "API 1",
                "count": len(results),
                "bookings": results
            })
            return

        # API 2: Get one booking
        prefix = "/api/booking/bookings/"

        if path.startswith(prefix):
            booking_ref = path[len(prefix):].upper()

            booking = next(
                (
                    b for b in BOOKINGS
                    if b["bookingRef"] == booking_ref
                ),
                None
            )

            if booking is None:
                self.send_json(404, {
                    "api": "API 2",
                    "error": "Booking not found"
                })
                return

            amount = booking["amount"]
            fee = 299 if amount > 5000 else 199
            tax = round((amount - fee) * 0.18)
            base = amount - fee - tax

            self.send_json(200, {
                "api": "API 2",
                **booking,
                "fareBreakdown": {
                    "baseFare": base,
                    "taxes": tax,
                    "convenienceFee": fee,
                    "total": amount
                }
            })
            return

        self.send_json(404, {
            "error": "Unknown endpoint"
        })


if __name__ == "__main__":
    server = HTTPServer(
        (HOST, PORT),
        BookingAPIHandler
    )

    print(f"Booking API running at http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down Booking API.")
        server.server_close()
