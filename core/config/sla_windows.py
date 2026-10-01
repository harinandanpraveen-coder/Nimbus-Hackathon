from typing import Dict, Tuple

# Processing SLAs in minutes between upstream and downstream stages
# Key: (upstream_org, downstream_org) -> max_expected_minutes
STAGE_SLA_MINUTES: Dict[Tuple[str, str], float] = {
    ("Booking Platform", "Airline"): 120.0,         # 2 hours
    ("Airline", "Payment Provider"): 1440.0,       # 24 hours
    ("Payment Provider", "Issuing Bank"): 2880.0,  # 48 hours
}

DEFAULT_SLA_MINUTES: float = 1440.0