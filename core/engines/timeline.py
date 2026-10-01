from typing import List
from core.models.input_evidence import EvidenceRecord
from core.models.internal_state import TimelineEvent
from core.engines.normalizer import normalize_record_status


def build_timeline(records: List[EvidenceRecord]) -> List[TimelineEvent]:
    """Generates a sorted chronological timeline of events across source organizations."""
    if not records:
        return []

    # Sort evidence records chronologically by timestamp
    sorted_records = sorted(records, key=lambda r: r.timestamp)

    timeline = []
    for rec in sorted_records:
        norm_status = normalize_record_status(rec)
        timeline.append(
            TimelineEvent(
                source_organization=rec.source_organization.value,
                event=norm_status,
                source_status=rec.source_status,
                timestamp=rec.timestamp
            )
        )

    return timeline