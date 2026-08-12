import json

import ollama

from app.telemetry import configure_tracer
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


tracer = configure_tracer()


def execute_tool(tool_name, arguments):
    tool = TOOL_MAP.get(tool_name)

    if tool is None:
        return {
            "error": f"Unknown tool: {tool_name}"
        }

    with tracer.start_as_current_span(f"tool.{tool_name}") as span:
        span.set_attribute("tool.name", tool_name)

        for key, value in arguments.items():
            span.set_attribute(f"tool.argument.{key}", str(value))

        result = tool(**arguments)

        return result


def investigate(incident):
    with tracer.start_as_current_span("incident.investigation") as span:
        span.set_attribute("incident.id", incident["incident_id"])
        span.set_attribute("incident.title", incident["title"])

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