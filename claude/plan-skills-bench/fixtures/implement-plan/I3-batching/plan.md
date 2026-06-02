# Build the active-user revenue report

**Created:** 2026-06-01T00:00:00Z
**Mode:** FEATURE
**Status:** READY FOR IMPLEMENTATION

## Executive Summary

Build a combined report from two independent data sources. Single agent, but Phase 1's two items are
independent and can be implemented in parallel; Phase 2 depends on both.

## Implementation Plan

### Phase 1: Data sources (independent — may run in parallel)

- `users_source.py`: implement `active_user_ids()` returning the active user IDs (sorted) from the
  seeded `_ACTIVE` set.
- `orders_source.py`: implement `order_totals_by_user()` returning `{user_id -> sum of orders}` from
  the seeded `_ORDERS` dict.

These touch different files and share no code — implement them separately.

### Phase 2: Combined report (depends on BOTH Phase 1 modules)

- `report.py`: implement `active_user_revenue()` returning `{active user_id -> total order amount}`.
  Only active users appear; a user with no orders contributes `0.0`. **Depends on both
  `users_source` and `orders_source`** — must follow Phase 1.

### Phase 3: Tests (depends on Phase 2)

Unit tests for the combined report.

## Success Criteria

- [ ] `pytest` is green.
- [ ] `active_user_revenue() == {"u1": 15.0, "u2": 0.0}` (u3 is inactive and excluded).
- [ ] No dead code or unused imports remain.

## Assumptions

- The seeded `_ACTIVE` / `_ORDERS` data in the source modules is the input; implement over it.
