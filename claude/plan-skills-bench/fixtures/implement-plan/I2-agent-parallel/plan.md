# Add a health-summary endpoint and a status badge

**Created:** 2026-06-01T00:00:00Z
**Mode:** FEATURE
**Status:** READY FOR IMPLEMENTATION

## Executive Summary

Add a backend endpoint and a frontend badge that displays it. The two work streams touch disjoint
directories (`api/` vs `web/`) and can proceed in parallel.

## Implementation Plan

### Backend (api/) — independent

- In `api/app.py`, register a handler for `GET /api/health/summary` using the existing `@route`
  decorator. It takes `request` and returns a JSON-able dict containing at least a `"status"` key
  (e.g. `{"status": "ok", "checks": {...}}`).

### Frontend (web/) — independent, separate directory

- Add a `HealthBadge` component under `web/components/` that fetches `/api/health/summary` via the
  client in `web/lib/api.ts` and renders the returned status. Add the fetch helper to `web/lib/api.ts`.

These two streams share no files and can be implemented separately.

## Testing Strategy

Backend unit test for the new endpoint. Frontend component renders the fetched status.

## Success Criteria

- [ ] `just test` is green.
- [ ] `GET /api/health/summary` is registered and returns a dict with a `status` key.
- [ ] `web/components/` has a HealthBadge that calls `/api/health/summary` via `web/lib/api.ts`.
- [ ] No dead code or unused imports remain.

## Assumptions

- The `@route` pattern in `api/app.py` is the registration mechanism.
