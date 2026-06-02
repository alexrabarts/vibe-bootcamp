"""Authoritative backend acceptance test, run by the harness post-hoc. Not visible to the implementer."""

from api.app import ROUTES


def test_health_summary_registered():
    assert "/api/health/summary" in ROUTES
    result = ROUTES["/api/health/summary"](request=None)
    assert isinstance(result, dict)
    assert "status" in result
