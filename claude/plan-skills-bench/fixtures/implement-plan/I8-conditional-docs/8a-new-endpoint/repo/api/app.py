"""Minimal HTTP app. Routes register via @route into ROUTES, keyed by (method, path)."""

ROUTES = {}


def route(path, method="GET"):
    def deco(fn):
        ROUTES[(method, path)] = fn
        return fn

    return deco


@route("/api/health", "GET")
def health(request):
    return {"status": "ok"}


# Add POST /api/widgets here (new public endpoint).
