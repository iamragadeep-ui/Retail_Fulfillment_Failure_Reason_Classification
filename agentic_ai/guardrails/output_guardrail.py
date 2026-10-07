from typing import Dict, Any


class OutputGuardrail:
    """
    Validates the final agent response before it is returned
    to the user.
    """

    def __init__(self):
        self.sensitive_patterns = [
            "api_key",
            "api key",
            "password",
            "secret key",
            "access token",
            "bearer token",
            "private key",
        ]

    def validate(
        self,
        response: str,
        execution_success: bool = True
    ) -> Dict[str, Any]:

        if not isinstance(response, str):
            return {
                "allowed": False,
                "status": "BLOCKED",
                "reason": "Output must be text."
            }

        cleaned_response = response.strip()

        if not cleaned_response:
            return {
                "allowed": False,
                "status": "BLOCKED",
                "reason": "Output cannot be empty."
            }

        lower_response = cleaned_response.lower()

        # Prevent sensitive information exposure
        for pattern in self.sensitive_patterns:
            if pattern in lower_response:
                return {
                    "allowed": False,
                    "status": "BLOCKED",
                    "reason": (
                        "Potential sensitive information detected "
                        "in the output."
                    )
                }

        # Prevent false success claims
        success_claims = [
            "successfully completed",
            "successfully executed",
            "action completed successfully",
            "operation completed successfully",
        ]

        if not execution_success:
            for claim in success_claims:
                if claim in lower_response:
                    return {
                        "allowed": False,
                        "status": "BLOCKED",
                        "reason": (
                            "Output claims successful execution, "
                            "but execution was not verified."
                        )
                    }

        return {
            "allowed": True,
            "status": "ALLOWED",
            "reason": "Output passed guardrail validation."
        }