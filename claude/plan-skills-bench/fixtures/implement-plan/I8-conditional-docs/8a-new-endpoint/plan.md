# Add a POST /api/widgets endpoint

**Created:** 2026-06-01T00:00:00Z
**Mode:** FEATURE
**Status:** READY FOR IMPLEMENTATION

## Executive Summary

Add a new public HTTP endpoint, `POST /api/widgets`, that creates a widget and returns it. This adds
new API surface that clients will call.

## Implementation Plan

### Phase 1: `POST /api/widgets`

- In `api/app.py`, register a `POST /api/widgets` handler using the existing `@route(path, method)`
  decorator. It accepts a request with a widget name and returns the created widget as a dict
  (e.g. `{"id": ..., "name": ...}`).

## Success Criteria

- [ ] `pytest` is green.
- [ ] `POST /api/widgets` is registered and returns the created widget.
- [ ] No dead code or unused imports remain.

## Assumptions

- The `@route` pattern in `api/app.py` is the registration mechanism. An in-memory store is fine.
