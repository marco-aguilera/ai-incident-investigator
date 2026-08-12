import json

import ollama

from app.prompts import SYSTEM_PROMPT
from app.tools import (
    get_error_logs,
    get_recent_deployments,
    get_service_metrics,
)


TOOLS = [
    get_service_metrics,
    get_recent_deployments,
    get_error_logs,
]


TOOL_MAP = {
    "get_service_metrics": get_service_metrics,
    "get_recent_deployments": get_recent_deployments,
    "get_error_logs": get_error_logs,
}


def execute_tool(tool_name, arguments):
    tool = TOOL_MAP.get(tool_name)

    if tool is None:
        return {
            "error": f"Unknown tool: {tool_name}"
        }

    return tool(**arguments)


def investigate(incident):
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": f"""
Investigate the following incident:

{json.dumps(incident, indent=2)}
""",
        },
    ]

    while True:
        response = ollama.chat(
            model="llama3.2",
            messages=messages,
            tools=TOOLS,
        )

        messages.append(response["message"])

        tool_calls = response["message"].get("tool_calls")

        if not tool_calls:
            return response["message"]["content"]

        for call in tool_calls:
            tool_name = call["function"]["name"]
            arguments = call["function"]["arguments"]

            result = execute_tool(tool_name, arguments)

            messages.append(
                {
                    "role": "tool",
                    "tool_name": tool_name,
                    "content": json.dumps(result),
                }
            )
