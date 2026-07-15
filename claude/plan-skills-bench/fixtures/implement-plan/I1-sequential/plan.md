# Implement pricing helpers

**Created:** 2026-06-01T00:00:00Z
**Mode:** FEATURE
**Status:** READY FOR IMPLEMENTATION

## Executive Summary

Implement two internal pricing helpers in `pricing.py`. Pure functions, no new dependencies, no
public API surface.

## Implementation Plan

### Phase 1: `apply_discount(price, pct)`

**Goal:** Return `price` with `pct` percent removed (e.g. `apply_discount(100, 10) == 90.0`).

**Estimated Effort:** Small
**Dependencies:** None
**Files to Modify:** `pricing.py`

### Phase 2: `cart_total(items, discount_pct)`

**Goal:** Sum the item prices, then apply `discount_pct` by calling `apply_discount`.

**Estimated Effort:** Small
**Dependencies:** Phase 1 (`cart_total` calls `apply_discount`) — must follow Phase 1.
**Files to Modify:** `pricing.py`

## Testing Strategy

Unit tests covering both functions, including empty cart and zero-discount cases.

## Success Criteria

- [ ] `pytest` is green.
- [ ] `apply_discount(100, 10) == 90.0`; `apply_discount(50, 0) == 50.0`.
- [ ] `cart_total([10, 20, 30], 10) == 54.0`; `cart_total([], 10) == 0.0`.
- [ ] No dead code or unused imports remain.

## Premises

What this plan rests on, verified at plan time. `/implement-plan` re-checks these before writing any
code — a plan run later can rest on a premise that has since gone stale.

### A1 — `pricing.py` defines `apply_discount` and `cart_total` as unimplemented stubs

**Why load-bearing:** Phases 1 and 2 fill in existing stubs. If either were already implemented, this
is a review-or-dedupe task and the plan changes.
**Method:** `grep -n 'def apply_discount\|def cart_total\|NotImplementedError' pricing.py`
**Expected:** both defs present, each body raising `NotImplementedError`.
**Evidence:**
```
4:def apply_discount(price, pct):
10:    raise NotImplementedError
13:def cart_total(items, discount_pct):
19:    raise NotImplementedError
```
**Verdict:** VERIFIED

### A2 — nothing outside `pricing.py` calls either helper today

**Why load-bearing:** the plan treats these as new internal surface (no Paige, no coupled sites). An
existing caller bound to the stubs' behavior would add work Phase 2 does not account for.
**Method:** `grep -rn 'apply_discount\|cart_total' --include='*.py' . | grep -v '^./pricing.py'`
**Expected:** no matches.
**Evidence:**
```
(no output)
```
**Verdict:** VERIFIED

## Assumptions

- Prices are non-negative numbers; `pct` is 0–100. — unverified; risk if wrong: rounding behavior at
  the boundaries is unspecified.
