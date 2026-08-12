import json
from pathlib import Path

from app.agent import investigate


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_incident():
    incident_path = PROJECT_ROOT / "data" / "incidents" / "api-latency.json"

    with incident_path.open() as file:
        return json.load(file)


def main():
    incident = load_incident()

    print(f"Investigating: {incident['incident_id']}")
    print(f"Title: {incident['title']}")
    print()

    report = investigate(incident)

    print("\nInvestigation Report:\n")
    print(report)


if __name__ == "__main__":
    main()
