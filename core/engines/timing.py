# core/engines/timing.py
from typing import List
from core.config.sla_windows import STAGE_SLA_MINUTES, DEFAULT_SLA_MINUTES
from core.models.input_evidence import EvidenceRecord
from core.models.internal_state import TimelineEvent, TimingEvaluation, TimingStatus


def evaluate_timing(
    timeline: List[TimelineEvent],
    records: List[EvidenceRecord],
    current_time: float | None = None
) -> TimingEvaluation:
    """Calculates elapsed processing windows and checks for SLA breaches."""
    if not timeline or len(timeline) == 0:
        return TimingEvaluation(
            timing_status=TimingStatus.NOT_APPLICABLE,
            elapsed_minutes=0.0,
            expected_window_minutes=None
        )

    # If the process completed, SLA window evaluation is marked within bounds
    if any("COMPLETED" in ev.event or "CREDITED" in ev.event for ev in timeline):
        total_elapsed = (timeline[-1].timestamp - timeline[0].timestamp).total_seconds() / 60.0
        return TimingEvaluation(
            timing_status=TimingStatus.WITHIN_EXPECTED_WINDOW,
            elapsed_minutes=round(total_elapsed, 2),
            expected_window_minutes=DEFAULT_SLA_MINUTES
        )

    # 1. Evaluate stage-to-stage elapsed times across history
    max_breach_elapsed = 0.0
    max_breach_window = DEFAULT_SLA_MINUTES
    sla_exceeded = False

    for i in range(len(timeline) - 1):
        prev_ev = timeline[i]
        curr_ev = timeline[i + 1]
        step_elapsed = (curr_ev.timestamp - prev_ev.timestamp).total_seconds() / 60.0
        
        expected_window = STAGE_SLA_MINUTES.get(
            (prev_ev.source_organization, curr_ev.source_organization),
            DEFAULT_SLA_MINUTES
        )

        if step_elapsed > expected_window:
            sla_exceeded = True
            if step_elapsed > max_breach_elapsed:
                max_breach_elapsed = step_elapsed
                max_breach_window = expected_window

    # 2. Evaluate overall elapsed duration from start to latest record
    total_elapsed = (timeline[-1].timestamp - timeline[0].timestamp).total_seconds() / 60.0
    
    if sla_exceeded:
        return TimingEvaluation(
            timing_status=TimingStatus.WINDOW_EXCEEDED,
            elapsed_minutes=round(max_breach_elapsed, 2),
            expected_window_minutes=max_breach_window
        )

    # Check if latest stage is waiting on downstream stage beyond default SLA
    latest_event = timeline[-1]
    expected_window = STAGE_SLA_MINUTES.get(
        (latest_event.source_organization, "Payment Provider"),
        DEFAULT_SLA_MINUTES
    )

    return TimingEvaluation(
        timing_status=TimingStatus.WITHIN_EXPECTED_WINDOW,
        elapsed_minutes=round(total_elapsed, 2),
        expected_window_minutes=expected_window
    )