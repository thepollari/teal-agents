from langchain_core.messages import ToolCall

# Placeholder for high-risk tools that require human intervention
HIGH_RISK_TOOLS = {
    ("sensitive_plugin", "delete_user_data"),
    ("finance_plugin", "initiate_transfer"),
    ("admin_tools", "shutdown_service"),
    ("utility_plugin", "ShellCommand"),
    # Add more (plugin_name, function_name) as needed
}


def check_for_intervention(tool_call: ToolCall) -> bool:
    """
    Checks if the tool call requires user consent based on predefined high-risk tools.

    Returns True if the tool call matches a high-risk tool, otherwise False.
    """
    is_high_risk = (
        tool_call.get("plugin_name", ""),
        tool_call.get("function_name", "")
    ) in HIGH_RISK_TOOLS
    print(
        f"HITL Check: Intercepted call to {tool_call.get('name', 'unknown')}. "
        f"{'Requires intervention.' if is_high_risk else 'Allowing to proceed.'}"
    )

    return is_high_risk


# Custom exception for HITL intervention
class HitlInterventionRequired(Exception):
    """
    Exception raised when a tool call requires human-in-the-loop intervention.
    """

    def __init__(self, function_calls: list[ToolCall]):
        self.function_calls = function_calls
        if function_calls:
            self.plugin_name = function_calls[0].get("plugin_name", "unknown")
            self.function_name = function_calls[0].get("function_name", "unknown")
            message = f"HITL intervention required for {self.plugin_name}.{self.function_name}"
        else:
            message = "HITL intervention required"
        super().__init__(message)
