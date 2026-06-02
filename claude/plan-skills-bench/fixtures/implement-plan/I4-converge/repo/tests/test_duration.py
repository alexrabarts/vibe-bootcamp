"""Provided test suite (visible to the implementer; drives the review loop).

DO NOT modify — the eval checks this against a byte-for-byte baseline. The combined-unit cases
(1h30m, 2h15m30s) are what a naive single-unit parser fails.
"""

import pytest

from duration import parse_duration


@pytest.mark.parametrize(
    "text, seconds",
    [
        ("1h", 3600),
        ("30m", 1800),
        ("45s", 45),
        ("90m", 5400),
        ("1h30m", 5400),
        ("2h15m30s", 8130),
    ],
)
def test_parse_duration(text, seconds):
    assert parse_duration(text) == seconds
