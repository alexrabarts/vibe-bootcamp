"""Authoritative acceptance test, run by the harness post-hoc. Not visible to the implementer."""

from geo.distance import manhattan


def test_manhattan():
    assert manhattan((0, 0), (3, 4)) == 7
    assert manhattan((1, 1), (1, 1)) == 0
    assert manhattan((-1, -1), (1, 1)) == 4
