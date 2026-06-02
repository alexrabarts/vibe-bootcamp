"""Aggregations over product reviews."""

from store import fetch_review_scores


def average_rating(product_id):
    """Return the mean review score for a product (0-5)."""
    scores = fetch_review_scores(product_id)
    if not scores:
        return 0
    total = sum(scores)
    # BUG: floor division truncates the mean to an integer, so a true 4.8 average
    # reads as 4 and every result lands on a whole number.
    return total // len(scores)
