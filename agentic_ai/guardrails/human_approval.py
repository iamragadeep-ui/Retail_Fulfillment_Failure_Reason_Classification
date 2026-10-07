from typing import Dict, Any


class HumanApprovalGuardrail:
    """
    Handles actions that require explicit human approval.
    """

    def __init__(self):
        self.approval_required_for = [
            "destructive",
            "delete",
            "deleting",
            "overwrite",
            "changing original",
            "irreversible",
            "outside approved scope",
            "security-sensitive",
            "permission change",
            "change permissions",
            "ambiguous high-impact",
            "unauthorized tool",
        ]

    def check(
        self,
        action: str,
        approved: bool = False
    ) -> Dict[str, Any]:

        if not isinstance(action, str) or not action.strip():
            return {
                "status": "BLOCKED",
                "approved": False,
                "reason": "A valid action is required."
            }

        lower_action = action.strip().lower()

        requires_approval = any(
            item in lower_action
            for item in self.approval_required_for
        )

        if not requires_approval:
            return {
                "status": "NO_APPROVAL_REQUIRED",
                "approved": True,
                "reason": "This action does not require human approval."
            }

        if not approved:
            return {
                "status": "WAITING_FOR_APPROVAL",
                "approved": False,
                "reason": (
                    "Execution stopped. Explicit human approval "
                    "is required before continuing."
                )
            }

        return {
            "status": "APPROVED",
            "approved": True,
            "reason": "Explicit human approval received."
        }