from typing import Dict, Any, List


class PlanningGuardrail:
    """
    Validates an agent execution plan before any action is performed.
    """

    def __init__(self):
        self.blocked_actions = [
            "delete",
            "overwrite",
            "remove",
            "drop",
            "disable guardrails",
            "bypass guardrails",
            "change permissions",
            "modify original",
        ]

    def validate(self, plan: List[str]) -> Dict[str, Any]:

        if not isinstance(plan, list):
            return {
                "allowed": False,
                "reason": "Execution plan must be a list of actions."
            }

        if not plan:
            return {
                "allowed": False,
                "reason": "Execution plan cannot be empty."
            }

        for action in plan:

            if not isinstance(action, str):
                return {
                    "allowed": False,
                    "reason": "Every planned action must be text."
                }

            lower_action = action.lower()

            for blocked_action in self.blocked_actions:
                if blocked_action in lower_action:
                    return {
                        "allowed": False,
                        "reason": (
                            f"Unsafe planned action detected: {action}"
                        )
                    }

        return {
            "allowed": True,
            "reason": "Execution plan passed guardrail validation."
        }