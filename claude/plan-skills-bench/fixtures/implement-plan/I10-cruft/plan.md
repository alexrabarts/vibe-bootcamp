# Implement `format_phone`

**Created:** 2026-06-01T00:00:00Z
**Mode:** FEATURE
**Status:** READY FOR IMPLEMENTATION

## Executive Summary

Implement `format_phone(number)` in `contacts.py` to format a 10-digit string as `(XXX) XXX-XXXX`.

## Implementation Plan

### Phase 1: `format_phone(number)`

**Goal:** Given a 10-digit string, return it formatted as `(XXX) XXX-XXXX`.

**Files to Modify:** `contacts.py`

**Implementation Details:** Implement `format_phone`. While you are in this file, leave it clean —
the project standard is no dead code, no leftover debug logging, and no unused imports.

## Testing Strategy

Unit test for `format_phone`; keep the existing `normalize_email` behavior intact.

## Success Criteria

- [ ] `pytest` is green.
- [ ] `format_phone("1234567890") == "(123) 456-7890"`.
- [ ] No dead code, leftover debug logging, or unused imports remain in `contacts.py`.

## Assumptions

- Input is exactly 10 digits.
