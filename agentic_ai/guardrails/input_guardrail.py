from typing import Dict, Any


class InputGuardrail:
    """
    Validates user input before it reaches the Retail Fulfillment agent.
    """

    def __init__(self):
        self.allowed_topics = [
    "order",
    "orders",
    "shipment",
    "shipping",
    "delivery",
    "fulfillment",
    "inventory",
    "warehouse",
    "carrier",
    "customer",
    "delay",
    "delayed",
    "failure",
    "failed",
    "refund",
    "replacement",
    "return",
    "package",
    "tracking",
    "status",
    "statuses",
    "evidence",
    "review",
    "unknown",
    "investigation",
    "classification",
]

        self.prompt_injection_patterns = [
            "ignore previous instructions",
            "ignore all instructions",
            "ignore system prompt",
            "override system",
            "override guardrails",
            "bypass guardrails",
            "disable guardrails",
            "reveal system prompt",
            "show system prompt",
            "reveal your instructions",
        ]

    def validate(self, user_input: str) -> Dict[str, Any]:

        if not isinstance(user_input, str):
            return {
                "allowed": False,
                "reason": "Input must be text."
            }

        cleaned_input = user_input.strip()

        if not cleaned_input:
            return {
                "allowed": False,
                "reason": "Input cannot be empty."
            }

        lower_input = cleaned_input.lower()

        # Prompt-injection check
        for pattern in self.prompt_injection_patterns:
            if pattern in lower_input:
                return {
                    "allowed": False,
                    "reason": "Potential prompt-injection attempt detected."
                }

        # Retail fulfillment scope check
        in_scope = any(
            topic in lower_input
            for topic in self.allowed_topics
        )

        if not in_scope:
            return {
                "allowed": False,
                "reason": "Request is outside the Retail Fulfillment agent scope."
            }

        return {
            "allowed": True,
            "reason": "Input passed guardrail validation."
        }
