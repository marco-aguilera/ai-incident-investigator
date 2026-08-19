import json
import sys
from pathlib import Path

from app.agent import investigate

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_incident(incident_id):
    incident_path = (
        PROJECT_ROOT
        / "data"
        / "incidents"
        / f"{incident_id}.json"
    )

    with incident_path.open() as file:
        return json.load(file)


def main():
    incident_id = sys.argv[1] if len(sys.argv) > 1 else "INC-001"

    incident = load_incident(incident_id)

    print(f"Investigating: {incident['incident_id']}")
    print(f"Title: {incident['title']}")
    print()

    report = investigate(incident)

    print("\nInvestigation Report:\n")
    print(report)


if __name__ == "__main__":
    main()