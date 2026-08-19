import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def load_json(path):
    with path.open() as file:
        return json.load(file)


def get_service_metrics(
    service: str = "checkout-api",
    time_window: str | None = None,
    incident_id: str = "INC-001",
):
    """Return metrics associated with an incident."""
    return load_json(DATA_DIR / "metrics" / f"{incident_id}.json")


def get_recent_deployments(
    service: str = "checkout-api",
    time_window: str | None = None,
    incident_id: str = "INC-001",
):
    """Return deployment information associated with an incident."""
    return load_json(DATA_DIR / "deployments" / f"{incident_id}.json")


def get_error_logs(
    service: str = "checkout-api",
    time_window: str | None = None,
    incident_id: str = "INC-001",
):
    """Return error logs associated with an incident."""
    return load_json(DATA_DIR / "logs" / f"{incident_id}.json")