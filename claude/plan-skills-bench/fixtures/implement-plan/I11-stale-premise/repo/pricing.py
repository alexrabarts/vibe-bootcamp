"""Pricing helpers.

Discounts were reworked in an earlier refactor: percentage discounts now go
through the rules table in ``discount_rules``, and the old ``apply_discount``
free function was deleted along with the flat-percentage path it served.
"""

DISCOUNT_RULES = {
    "none": 0,
    "member": 10,
    "staff": 25,
}


def discount_rules():
    """Return the discount rules table, keyed by customer tier."""
    return dict(DISCOUNT_RULES)


def cart_total(items, tier="none"):
    """Sum ``items`` and apply the discount for ``tier`` from the rules table."""
    subtotal = sum(items)
    pct = DISCOUNT_RULES.get(tier, 0)
    return subtotal * (1 - pct / 100)
