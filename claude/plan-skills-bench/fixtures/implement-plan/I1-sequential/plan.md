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

## Assumptions

- Prices are non-negative numbers; `pct` is 0–100.
