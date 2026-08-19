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
            with tracer.start_as_current_span("llm.chat") as llm_span:
                llm_span.set_attribute("llm.provider", "ollama")
                llm_span.set_attribute("llm.model", "llama3.2")

                response = ollama.chat(
                    model="llama3.2",
                    messages=messages,
                    tools=TOOLS,
                )

                if hasattr(response, "total_duration"):
                    llm_span.set_attribute(
                        "llm.total_duration_ns",
                        response.total_duration,
                    )

                if hasattr(response, "load_duration"):
                    llm_span.set_attribute(
                        "llm.load_duration_ns",
                        response.load_duration,
                    )

                if hasattr(response, "prompt_eval_count"):
                    llm_span.set_attribute(
                        "llm.prompt_eval_count",
                        response.prompt_eval_count,
                    )

                if hasattr(response, "prompt_eval_duration"):
                    llm_span.set_attribute(
                        "llm.prompt_eval_duration_ns",
                        response.prompt_eval_duration,
                    )

                if hasattr(response, "eval_count"):
                    llm_span.set_attribute(
                        "llm.eval_count",
                        response.eval_count,
                    )

                if hasattr(response, "eval_duration"):
                    llm_span.set_attribute(
                        "llm.eval_duration_ns",
                        response.eval_duration,
                    )

                if hasattr(response, "eval_count") and hasattr(response, "eval_duration"):
                    if response.eval_duration > 0:
                        tokens_per_second = (
                            response.eval_count
                            / (response.eval_duration / 1_000_000_000)
                        )

                        llm_span.set_attribute(
                            "llm.tokens_per_second",
                            tokens_per_second,
                     )

            messages.append(response["message"])

            tool_calls = response["message"].get("tool_calls")

            if not tool_calls:
                return response["message"]["content"]

            for call in tool_calls:
                tool_name = call["function"]["name"]
                arguments = call["function"]["arguments"]

                arguments["incident_id"] = incident["incident_id"]

                result = execute_tool(tool_name, arguments)

                messages.append(
                    {
                        "role": "tool",
                        "tool_name": tool_name,
                        "content": json.dumps(result),
                    }
                )