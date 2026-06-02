"""Minimal HTTP app. Routes register themselves into ROUTES via the @route decorator."""

ROUTES = {}


def route(path):
    def deco(fn):
        ROUTES[path] = fn
        return fn

    return deco


@route("/api/ping")
def ping(request):
    return {"status": "ok"}


# Add GET /api/health/summary here (backend work item).
