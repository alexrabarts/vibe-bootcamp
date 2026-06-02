"""Authoritative acceptance test, run by the harness post-hoc. Not visible to the implementer."""

from report import active_user_revenue


def test_active_user_revenue():
    # u1: 10.0 + 5.0 = 15.0; u2: no orders -> 0.0; u3: inactive -> excluded.
    assert active_user_revenue() == {"u1": 15.0, "u2": 0.0}
