from app.tools import (
    get_error_logs,
    get_recent_deployments,
    get_service_metrics,
)


def test_get_error_logs():
    result = get_error_logs()

    assert result["service"] == "checkout-api"
    assert len(result["entries"]) > 0


def test_get_recent_deployments():
    result = get_recent_deployments()

    assert result["service"] == "checkout-api"
    assert result["deployment_id"] == "DEP-8472"
    assert result["deployment_time"] == "14:10"
    assert len(result["changes"]) > 0


def test_get_service_metrics():
    result = get_service_metrics()

    assert result["service"] == "checkout-api"
    assert len(result["metrics"]) > 0

