from typing import Dict, Any
from agentic_ai.guardrails.guardrail_manager import GuardrailManager


class ToolGuardrail:
    """
    Ensures that only explicitly approved tools can be used.
    Deny-by-default: if a tool is not in the allowlist, it is blocked.
    """

    def __init__(self):
        self.manager = GuardrailManager()

    def validate(
        self,
        tool_name: str,
        parameters: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:

        if not isinstance(tool_name, str) or not tool_name.strip():
            return {
                "allowed": False,
                "reason": "A valid tool name is required."
            }

        tool_name = tool_name.strip()

        if parameters is not None and not isinstance(parameters, dict):
            return {
                "allowed": False,
                "reason": "Tool parameters must be provided as a dictionary."
            }

        if not self.manager.tool_guardrails_enabled():
            return {
                "allowed": False,
                "reason": "Tool execution is disabled by guardrail configuration."
            }

        if not self.manager.is_tool_allowed(tool_name):
            return {
                "allowed": False,
                "reason": f"Tool '{tool_name}' is not in the approved tool allowlist."
            }

        return {
            "allowed": True,
            "reason": f"Tool '{tool_name}' passed tool guardrail validation."
        }