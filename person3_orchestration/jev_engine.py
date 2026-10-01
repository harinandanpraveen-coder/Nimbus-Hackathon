from typing import Any, Dict, Optional
from src.models.application_case import JevDecisionAssessment
from src.models.refund_case import RefundCase
from person3_orchestration.fallback import FallbackGenerator
from person3_orchestration.guardrails import GuardrailsValidator, HallucinationGuardrailError


class JevDecisionEngine:
    """Decision Advisory & Explanation Engine powered by Jev."""

    def __init__(self, api_client: Optional[Any] = None):
        self.api_client = api_client

    def evaluate_case(self, facts_payload: Dict[str, Any], refund_case: Any) -> JevDecisionAssessment:
        if not self.api_client:
            # If no live client is injected, invoke deterministic fallback
            return FallbackGenerator.generate_fallback(refund_case)

        try:
            # Structured prompt for Jev
            prompt = f"""
            System: You are Jev, an expert operations decision advisor.
            Evaluate the following reconciled refund case facts and generate structured decision assessment.
            STRICT RULES:
            - Do NOT contradict the normalized state ({facts_payload['normalized_state']}).
            - Ground all statements strictly in the provided timeline and evidence.

            Facts Payload:
            {facts_payload}
            """

            # Simulated API response call
            raw_response = self.api_client.generate_structured(
                prompt=prompt, schema=JevDecisionAssessment
            )

            # Validate output against guardrails
            GuardrailsValidator.validate(raw_response, refund_case)
            return raw_response

        except (Exception, HallucinationGuardrailError):
            # Safe failover to deterministic fallback on error or guardrail failure
            return FallbackGenerator.generate_fallback(refund_case)
