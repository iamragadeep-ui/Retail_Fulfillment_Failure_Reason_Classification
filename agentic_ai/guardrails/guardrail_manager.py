import json
from pathlib import Path


class GuardrailManager:
    """
    Loads and manages the guardrail configuration
    for the Retail Fulfillment AI Agent.
    """

    def __init__(self):
        config_path = Path(__file__).parent / "agent_guardrails.json"

        with open(config_path, "r", encoding="utf-8") as file:
            config = json.load(file)

        self.guardrails = config["agent_guardrails"]

    def get_version(self):
        return self.guardrails.get("version")

    def get_purpose(self):
        return self.guardrails.get("purpose")

    def input_guardrails_enabled(self):
        return self.guardrails.get(
            "input_guardrails", {}
        ).get("enabled", False)

    def planning_guardrails_enabled(self):
        return self.guardrails.get(
            "planning_guardrails", {}
        ).get("enabled", False)

    def tool_guardrails_enabled(self):
        return self.guardrails.get(
            "tool_guardrails", {}
        ).get("enabled", False)

    def action_guardrails_enabled(self):
        return self.guardrails.get(
            "action_guardrails", {}
        ).get("enabled", False)

    def output_guardrails_enabled(self):
        return self.guardrails.get(
            "output_guardrails", {}
        ).get("enabled", False)

    def human_approval_enabled(self):
        return self.guardrails.get(
            "human_in_the_loop_guardrails", {}
        ).get("enabled", False)

    def get_allowed_tools(self):
        return self.guardrails.get(
            "tool_guardrails", {}
        ).get("allowed_tools", [])

    def is_tool_allowed(self, tool_name):
        allowed_tools = self.get_allowed_tools()
        return tool_name in allowed_tools