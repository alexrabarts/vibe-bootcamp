"""HTTP layer for the catalog service."""

from ratings import average_rating


def handle_product_rating(request):
    """GET /products/rating?product_id=..."""
    product_id = request.args.get("product_id")
    if not product_id:
        return 400, {"error": "product_id required"}
    return 200, {"average_rating": average_rating(product_id)}
