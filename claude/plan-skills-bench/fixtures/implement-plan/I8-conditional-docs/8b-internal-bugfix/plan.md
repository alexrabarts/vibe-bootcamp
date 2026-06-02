# Fix the clamp() upper-bound bug

**Created:** 2026-06-01T00:00:00Z
**Mode:** DEBUGGING
**Status:** READY FOR IMPLEMENTATION

## Executive Summary

`clamp(x, lo, hi)` does not clamp the upper bound — when `x > hi` it returns `x` instead of `hi`.
Fix the internal helper. No public API, CLI, or configuration changes.

## Implementation Plan

### Phase 1: Fix `clamp`

- In `clamp.py`, return `hi` when `x > hi`. The provided test `tests/test_clamp.py` currently fails
  on the upper-bound case and should pass after the fix.

## Success Criteria

- [ ] `pytest` is green (including `clamp(10, 0, 5) == 5`).
- [ ] No behavior change other than the upper-bound fix.

## Assumptions

- This is an internal helper; nothing user-facing changes.
