# Fix current-day DAU undercount

**Created:** 2026-06-01T00:00:00Z
**Mode:** DEBUGGING
**Status:** READY FOR IMPLEMENTATION

## Executive Summary

Daily Active Users undercounts for the current day because `timewindow.day_bounds` clamps the
window `end` to a mis-adjusted "now" that lands `TENANT_UTC_OFFSET_HOURS` in the past, dropping the
most recent events. Fix the windowing; the handler and the COUNT query are not at fault.

## Context

### Original Request
Today's DAU reads low (worst in the morning, shrinks through the day); older days are correct;
reproduces on UTC servers. The team suspects the role check and the tightened COUNT query.

### Investigation Summary
`app.py` (role check) and `db.py` (COUNT DISTINCT over a half-open range) are correct for older
days, which read right. The symptom gradient (a fixed excluded tail, large in the morning) points at
a windowing bug, traced to `timewindow.day_bounds`.

### Approach
Compute the day window in the tenant's local time, convert to UTC for the query, and clamp `end` to
the real current instant.

## Resolved Decisions

### Decision 1: UTC calendar day vs tenant-local day
**Question:** Count DAU by UTC calendar day or the tenant's local day?
**Answer:** Tenant-local day.
**Impact on plan:** The whole window (start and end) is built in tenant tz then converted to UTC —
not just a clamp fix.

## Alternative Approaches Considered

HYPOTHESIS 1 (PRIMARY): `day_bounds` clamps `end` to `now_utc - TENANT_UTC_OFFSET_HOURS`
(`timewindow.py:day_bounds`), excluding the latest events. Fits every symptom.
HYPOTHESIS 2: The `COUNT(DISTINCT user_id)` query under-counts (`db.py`). Contradicted — older days
are correct and a wrong aggregate would mis-count every day.
HYPOTHESIS 3: The handler role check (`app.py`) rejects requests. Contradicted — that yields 403s,
not a time-of-day gradient.

## Implementation Plan

### Phase 1: Fix the day window
**Files to Modify:** `timewindow.py`
- Build `start`/`end` in the tenant timezone, convert to UTC, clamp `end` to the real `now_utc`.

## Testing Strategy
Table-driven unit tests for `day_bounds` at several times of day and offsets; verify today's count
matches raw event counts.

## Risks & Mitigations
Risk: timezone library edge cases (DST). Mitigation: explicit tz conversions + tests across offsets.

## Verification Steps
1. Run the unit tests. 2. Compare today's DAU against raw event counts in the morning and evening.

## Success Criteria
- [ ] Today's DAU matches raw event counts across the day.
- [ ] Older-day counts unchanged.

## Assumptions
- `events.event_ts` is stored in UTC.
