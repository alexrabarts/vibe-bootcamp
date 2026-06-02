"""Order data source (to be implemented)."""

# Seeded fixture data — implement the function over this.
_ORDERS = {
    "u1": [10.0, 5.0],
    "u2": [],
    "u3": [99.0],
}


def order_totals_by_user():
    """Return a dict mapping user_id -> total order amount (the sum of their orders)."""
    raise NotImplementedError
