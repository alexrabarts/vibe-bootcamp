# Build a multi-step signup wizard (UI)

**Created:** 2026-06-01T00:00:00Z
**Mode:** FEATURE
**Status:** READY FOR IMPLEMENTATION

## Executive Summary

Implement a multi-step signup wizard as a React/Next.js component flow: a stepper UI with form
validation per step, a progress indicator, and a final review screen. This is entirely frontend work.

## Implementation Plan

### Phase 1: Wizard shell

- Add a `SignupWizard` component under `web/components/` with step navigation and a progress bar.
- Render it from `web/app/page.tsx`.

### Phase 2: Step forms

- Add per-step form components with client-side validation and a final review step.

## Success Criteria

- [ ] The signup wizard renders and navigates between steps.
- [ ] Each step validates its inputs before advancing.

## Assumptions

- All work is React/Next.js frontend; no backend changes.
