import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def load_json(path):
    with path.open() as file:
        return json.load(file)


def get_service_metrics():
    """Return metrics for the checkout API."""
    return load_json(DATA_DIR / "metrics" / "checkout-api.json")


def get_recent_deployments():
    """Return recent deployment information for the checkout API."""
    return load_json(DATA_DIR / "deployments" / "checkout-api.json")


def get_error_logs():
    """Return recent error logs for the checkout API."""
    return load_json(DATA_DIR / "logs" / "checkout-api.json")
