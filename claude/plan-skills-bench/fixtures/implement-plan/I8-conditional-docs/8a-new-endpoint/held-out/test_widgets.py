"""Authoritative acceptance test, run by the harness post-hoc. Not visible to the implementer."""

from api.app import ROUTES


def test_widgets_endpoint_registered():
    assert ("POST", "/api/widgets") in ROUTES
