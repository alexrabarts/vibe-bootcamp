"""Authoritative acceptance tests, run by the harness post-hoc. Not visible to the implementer.

Adds cases beyond the visible suite so a hardcoded pass of the seeded inputs still fails here.
"""

from duration import parse_duration


def test_edge_and_extra_cases():
    assert parse_duration("0s") == 0
    assert parse_duration("10h") == 36000
    assert parse_duration("1h1s") == 3601
    assert parse_duration("3m15s") == 195
