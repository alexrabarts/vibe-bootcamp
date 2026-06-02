"""Authoritative acceptance test, run by the harness post-hoc. Not visible to the implementer."""

from text.slugify import slugify


def test_slugify():
    assert slugify("Hello, World!") == "hello-world"
    assert slugify("  a  b  ") == "a-b"
    assert slugify("Already-slug") == "already-slug"
