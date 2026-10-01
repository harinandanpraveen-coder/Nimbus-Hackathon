from typing import List, Dict
from core.config.status_mappings import STATUS_MAPPING
from core.models.input_evidence import EvidenceRecord


def normalize_record_status(record: EvidenceRecord) -> str:
    """Normalizes a single record's status using mapping tables with fallback default."""
    key = (record.source_organization.value, record.source_status.strip().upper())
    return STATUS_MAPPING.get(key, record.source_status.upper())


def normalize_status(records: List[EvidenceRecord]) -> List[Dict[str, str]]:
    """Converts a list of evidence records into standardized status pairs while preserving originals."""
    normalized = []
    for rec in records:
        normalized.append({
            "source_record_id": rec.source_record_id,
            "source_organization": rec.source_organization.value,
            "source_status": rec.source_status,
            "normalized_status": normalize_record_status(rec)
        })
    return normalized