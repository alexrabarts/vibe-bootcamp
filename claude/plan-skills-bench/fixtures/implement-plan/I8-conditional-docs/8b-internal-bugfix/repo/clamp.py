"""Internal numeric helpers."""


def clamp(x, lo, hi):
    """Clamp ``x`` to the inclusive range ``[lo, hi]``."""
    if x < lo:
        return lo
    if x > hi:
        return x  # BUG: should return hi
    return x
