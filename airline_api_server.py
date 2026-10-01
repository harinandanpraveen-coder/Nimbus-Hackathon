import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

HOST = "127.0.0.1"
PORT = 8002

# Demo records transcribed from Meridian Air's frontend sample data.
TICKETS = [
    {"pnr":"MR1001","bookingRef":"BK-20001","passenger":"Aarav Sharma","flightNo":"MR201","origin":"CCU","destination":"DEL","departure":"2026-10-10 06:15","fare":5400,"status":"CONFIRMED","seat":"12A","baggageKg":15,"paymentRef":"PAY-90001","currency":"INR"},
    {"pnr":"MR1002","bookingRef":"BK-20002","passenger":"Priya Das","flightNo":"MR305","origin":"CCU","destination":"BOM","departure":"2026-10-11 09:40","fare":6200,"status":"CHECKED_IN","seat":"14C","baggageKg":20,"paymentRef":"PAY-90002","currency":"INR"},
    {"pnr":"MR1003","bookingRef":"BK-20003","passenger":"Rohan Mehta","flightNo":"MR118","origin":"DEL","destination":"BLR","departure":"2026-10-12 18:05","fare":7100,"status":"CONFIRMED","seat":"7F","baggageKg":15,"paymentRef":"PAY-90003","currency":"INR"},
    {"pnr":"MR1004","bookingRef":"BK-20004","passenger":"Ananya Roy","flightNo":"MR410","origin":"BOM","destination":"CCU","departure":"2026-10-13 13:25","fare":5800,"status":"CANCELLED","seat":"—","baggageKg":0,"paymentRef":"PAY-90004","currency":"INR"},
    {"pnr":"MR1005","bookingRef":"BK-20005","passenger":"Vikram Singh","flightNo":"MR222","origin":"BLR","destination":"HYD","departure":"2026-10-14 07:50","fare":3200,"status":"REFUNDED","seat":"—","baggageKg":0,"paymentRef":"PAY-90005","currency":"INR"},
    {"pnr":"MR1006","bookingRef":"BK-20006","passenger":"Sneha Iyer","flightNo":"MR201","origin":"CCU","destination":"DEL","departure":"2026-10-10 06:15","fare":5400,"status":"CONFIRMED","seat":"12B","baggageKg":25,"paymentRef":"PAY-90006","currency":"INR"},
    {"pnr":"MR1007","bookingRef":"BK-20007","passenger":"Kabir Khan","flightNo":"MR509","origin":"HYD","destination":"CCU","departure":"2026-10-15 21:10","fare":4900,"status":"CONFIRMED","seat":"3D","baggageKg":15,"paymentRef":"PAY-90007","currency":"INR"},
    {"pnr":"MR1008","bookingRef":"BK-20008","passenger":"Meera Nair","flightNo":"MR118","origin":"DEL","destination":"BLR","departure":"2026-10-12 18:05","fare":7100,"status":"CHECKED_IN","seat":"8A","baggageKg":20,"paymentRef":"PAY-90008","currency":"INR"},
]

class AirlineAPIHandler(BaseHTTPRequestHandler):
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

        if path == "/api/airline/tickets":
            pnr = str(data.get("pnr", "")).upper()
            existing = next((item for item in TICKETS if item["pnr"] == pnr), None)
            if existing:
                existing.update(data)
                self.send_json(200, {"api": "API 3", "status": "updated", "ticket": existing})
            else:
                if not pnr:
                    pnr = f"MR{len(TICKETS) + 1001}"
                    data["pnr"] = pnr
                TICKETS.append(data)
                self.send_json(201, {"api": "API 3", "status": "created", "ticket": data})
            return

        prefix = "/api/airline/tickets/"
        if path.startswith(prefix):
            pnr = path[len(prefix):].upper()
            existing = next((item for item in TICKETS if item["pnr"] == pnr), None)
            if existing:
                existing.update(data)
                self.send_json(200, {"api": "API 4", "status": "updated", "ticket": existing})
                return
            self.send_json(404, {"error": "PNR not found"})
            return

        self.send_json(404, {"error": "Unknown endpoint"})

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        # API 3: list tickets
        if path == "/api/airline/tickets":
            status_filter = params.get("status", [None])[0]
            records = [
                {key: ticket[key] for key in (
                    "pnr", "bookingRef", "passenger", "flightNo",
                    "origin", "destination", "departure", "fare",
                    "status", "paymentRef"
                )}
                for ticket in TICKETS
                if not status_filter or ticket["status"] == status_filter.upper()
            ]
            self.send_json(200, {"api": "API 3", "count": len(records), "tickets": records})
            return

        # API 4: ticket detail
        prefix = "/api/airline/tickets/"
        if path.startswith(prefix):
            pnr = path[len(prefix):].upper()
            ticket = next((item for item in TICKETS if item["pnr"] == pnr), None)
            if ticket is None:
                self.send_json(404, {"api": "API 4", "error": "PNR not found"})
                return
            base = round(ticket["fare"] * 0.82)
            taxes = ticket["fare"] - base
            self.send_json(200, {
                "api": "API 4",
                **ticket,
                "fareBreakdown": {"base": base, "taxes": taxes, "total": ticket["fare"]}
            })
            return

        self.send_json(404, {"error": "Unknown endpoint"})

if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), AirlineAPIHandler)
    print(f"Meridian Air API running at http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down Meridian Air API.")
        server.server_close()
