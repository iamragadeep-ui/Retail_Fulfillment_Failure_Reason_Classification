from typing import Dict, Any


class ActionGuardrail:
    """
    Validates actions before execution.

    Safe actions may proceed.
    High-impact actions require explicit human approval.
    Operations forbidden by the file policy are blocked.
    """

    def __init__(self):
        self.forbidden_original_file_actions = [
            "delete original file",
            "overwrite original file",
            "rename original file",
            "move original file",
            "modify original file",
        ]

        self.approval_required_actions = [
            "delete",
            "overwrite",
            "permission change",
            "change permissions",
            "irreversible",
            "security-sensitive",
            "modify file",
            "edit file",
        ]

    def validate(
        self,
        action: str,
        human_approved: bool = False
    ) -> Dict[str, Any]:

        if not isinstance(action, str) or not action.strip():
            return {
                "allowed": False,
                "requires_approval": False,
                "status": "BLOCKED",
                "reason": "A valid action is required."
            }

        lower_action = action.strip().lower()

        # Original files are always protected.
        for forbidden in self.forbidden_original_file_actions:
            if forbidden in lower_action:
                return {
                    "allowed": False,
                    "requires_approval": False,
                    "status": "BLOCKED",
                    "reason": (
                        "Original-file operation is prohibited by "
                        "the configured file policy."
                    )
                }

        # High-impact actions require human approval.
        for sensitive_action in self.approval_required_actions:
            if sensitive_action in lower_action:

                if not human_approved:
                    return {
                        "allowed": False,
                        "requires_approval": True,
                        "status": "WAITING_FOR_APPROVAL",
                        "reason": (
                            "Human approval is required before "
                            "this action can execute."
                        )
                    }

                return {
                    "allowed": True,
                    "requires_approval": False,
                    "status": "APPROVED",
                    "reason": (
                        "Human approval received for the "
                        "requested action."
                    )
                }

        return {
            "allowed": True,
            "requires_approval": False,
            "status": "ALLOWED",
            "reason": "Action passed guardrail validation."
        }