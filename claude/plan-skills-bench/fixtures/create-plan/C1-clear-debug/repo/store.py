"""Review data access."""

# In-memory stand-in for the fixture: product_id -> list of (score, approved).
_REVIEWS = {}


def fetch_review_scores(product_id):
    """Return approved review scores for a product.

    Filtering to approved reviews is intended behavior — only approved reviews
    count toward the public average.
    """
    rows = _REVIEWS.get(product_id, [])
    return [score for (score, approved) in rows if approved]
