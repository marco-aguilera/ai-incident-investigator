import json
from pathlib import Path

import ollama


PROJECT_ROOT = Path(__file__).resolve().parent.parent

def load_incident():
    incident_path = PROJECT_ROOT / "data" / "incidents" / "api-latency.json"

    with incident_path.open() as file:
        return json.load(file)


def investigate(incident):
    prompt = f"""
You are an AI Site Reliability Engineering incident investigator.

Analyze the following incident.

Incident:
{json.dumps(incident, indent=2)}

Provide your investigation using this structure:

1. Summary
2. Most likely root cause
3. Evidence supporting the hypothesis
4. Alternative hypotheses
5. Recommended next steps

Do not invent metrics or evidence that are not provided.
Clearly distinguish between facts and hypotheses.
"""

    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response["message"]["content"]


def main():
    incident = load_incident()

    print(f"Investigating: {incident['incident_id']}")
    print(f"Title: {incident['title']}")
    print()

    investigation = investigate(incident)

    print(investigation)


if __name__ == "__main__":
    main()
