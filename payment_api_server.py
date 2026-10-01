import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

HOST = "127.0.0.1"
PORT = 8003
METHODS = ["UPI", "Credit Card", "Debit Card", "Net Banking"]

# Demo records transcribed from Zenpay's frontend sample data.
_PAYMENT_ROWS = [
    ("PAY-90001","BK-20001","MR1001","Aarav Sharma",5400,"SUCCESS","2026-10-01 10:13",0),
    ("PAY-90002","BK-20002","MR1002","Priya Das",6200,"SUCCESS","2026-10-01 11:41",0),
    ("PAY-90003","BK-20003","MR1003","Rohan Mehta",7100,"SUCCESS","2026-10-02 09:06",0),
    ("PAY-90004","BK-20004","MR1004","Ananya Roy",5800,"SUCCESS","2026-10-02 14:31",0),
    ("PAY-90005","BK-20005","MR1005","Vikram Singh",3200,"REFUNDED","2026-10-03 08:21",3200),
    ("PAY-90006","BK-20006","MR1006","Sneha Iyer",5400,"FAILED","2026-10-03 16:46",0),
    ("PAY-90007","BK-20007","MR1007","Kabir Khan",5100,"SUCCESS","2026-10-04 12:01",0),
    ("PAY-90008","BK-20008","MR1008","Meera Nair",7100,"SUCCESS","2026-10-04 19:11",0),
    ("PAY-90009","BK-20009","MR1009","Rahul Verma",5400,"SUCCESS","2026-10-05 07:56",0),
    ("PAY-90010","BK-20010","MR1010","Isha Patel",4500,"SUCCESS","2026-10-05 10:30",0),
]

TRANSACTIONS = [
    {
        "paymentRef": row[0], "bookingRef": row[1], "airlinePnr": row[2],
        "payer": row[3], "method": METHODS[i % len(METHODS)], "amount": row[4],
        "status": row[5], "paidAt": row[6], "refundedAmount": row[7],
        "currency": "INR", "gatewayTxnId": f"ZP{7300000 + i * 137}",
        "email": row[3].split()[0].lower() + "@example.com"
    }
    for i, row in enumerate(_PAYMENT_ROWS)
]

class PaymentAPIHandler(BaseHTTPRequestHandler):
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
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        # API 5: list transactions
        if path == "/api/payment/transactions":
            status_filter = params.get("status", [None])[0]
            records = [
                {key: txn[key] for key in (
                    "paymentRef", "bookingRef", "airlinePnr", "payer",
                    "method", "amount", "paidAt", "status"
                )}
                for txn in TRANSACTIONS
                if not status_filter or txn["status"] == status_filter.upper()
            ]
            self.send_json(200, {
                "api": "API 5", "count": len(records), "transactions": records
            })
            return

        # API 6: transaction detail
        prefix = "/api/payment/transactions/"
        if path.startswith(prefix):
            payment_ref = path[len(prefix):].upper()
            txn = next((item for item in TRANSACTIONS if item["paymentRef"] == payment_ref), None)
            if txn is None:
                self.send_json(404, {"api": "API 6", "error": "Payment not found"})
                return

            fee = 0 if txn["status"] == "FAILED" else round(txn["amount"] * 0.02)
            net = (
                txn["amount"] - fee if txn["status"] == "SUCCESS"
                else -fee if txn["status"] == "REFUNDED"
                else 0
            )
            self.send_json(200, {
                "api": "API 6", **txn,
                "gatewayFee": fee, "netSettlement": net
            })
            return

        self.send_json(404, {"error": "Unknown endpoint"})

if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), PaymentAPIHandler)
    print(f"Zenpay API running at http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down Zenpay API.")
        server.server_close()
