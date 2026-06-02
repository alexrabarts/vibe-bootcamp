# Dark-Mode Toggle on the Settings Page

**Created:** 2026-06-02
**Mode:** FEATURE (frontend / Next.js App Router)
**Status:** READY FOR IMPLEMENTATION

## Executive Summary

Add an accessible dark-mode switch to the settings page that flips the whole app between light and dark themes and remembers the choice across reloads without a flash of the wrong theme. The work extends the existing hand-rolled `ThemeProvider` (no new runtime dependency), wires it into a root layout via a render-blocking anti-flash script, and adds a minimal CSS-variable token layer so the change is visible end-to-end. Because the repo is currently a two-file skeleton with no build scaffold, a prerequisite scaffold phase is included.

## Context

### Original Request
> Add a dark-mode toggle to the settings page — a switch in Settings that flips the whole app between light and dark themes and remembers the choice across reloads. The settings page is `web/app/settings/page.tsx` and the theme context is in `web/components/ThemeProvider.tsx`.

### Investigation Summary
The repository is a **skeleton** — only two files exist and there is no build/runtime scaffold:

- `web/components/ThemeProvider.tsx` (`"use client"`): `type Theme = "light"` (light only); the context value is a bare string with **no setter**; the `useState` setter is discarded; there is **no persistence and no DOM application**. `useTheme()` returns the string.
- `web/app/settings/page.tsx` (**server** component): a placeholder `<section aria-label="Appearance" />` with the comment "Theme toggle will live here", and `className="settings"` despite no CSS existing.
- `ThemeProvider`/`useTheme` are **imported nowhere** — there is no `layout.tsx` wrapping the app.
- There is **no** `package.json`, `layout.tsx`, `globals.css`, `tsconfig.json`, `next.config.*`, Tailwind config, or any CSS. Single `baseline` commit.

**Implication:** "flips the *whole app*" and "remembers across reloads without a flash" cannot ride on existing infrastructure — there is none. The plan must add: a setter-bearing context (`light`|`dark`), single-source DOM application on `<html>`, validated persistence, render-blocking flash prevention, root-layout wiring, a CSS token layer, and the Next.js scaffold that makes all of it runnable and verifiable.

### Approach
**Approach 1 — Extend the hand-rolled provider + render-blocking anti-flash script + `localStorage`.** Binary `light`/`dark`. Add a minimal CSS-variable token layer and root-layout wiring so the toggle is visibly app-wide and testable. Selected as the default because it respects the existing `ThemeProvider.tsx` the request points to, adds no runtime dependency, and keeps full control. See **Alternative Approaches Considered** for the reviewer-recommended cookie-based variant.

## Resolved Decisions

The Phase 2.5 checkpoint questions were presented but **dismissed without selection**. Per protocol, each fork was resolved to its **recommended** option and recorded below as a defaulted decision. To change any of these, edit this section and the affected phase, then re-run `/implement-plan`.

### Decision 1: Persistence + flash handling
**Question:** How should persistence and flash-on-reload be handled?
**Answer (defaulted):** Extend the existing provider + render-blocking inline script + `localStorage`.
**Impact on plan:** Keeps `ThemeProvider.tsx`; requires a static inline script in the root layout and `suppressHydrationWarning` on `<html>`. No new dependency. (Reviewer-preferred alternative: cookie-based SSR — see Alternatives.)

### Decision 2: Theme modes
**Question:** What theme modes should the toggle expose?
**Answer (defaulted):** Binary `light`/`dark` switch (matches the word "switch").
**Impact on plan:** `type Theme = "light" | "dark"`; a single on/off control; no `prefers-color-scheme` resolution in v1 (deferred — see Assumptions).

### Decision 3: Styling scope
**Question:** How much styling infrastructure is in scope?
**Answer (defaulted):** Wire a root layout + a minimal `globals.css` token layer.
**Impact on plan:** Adds `web/app/layout.tsx` and `web/app/globals.css` with CSS-variable tokens and `.dark` overrides so the whole app visibly changes and the feature is end-to-end verifiable.

## Alternative Approaches Considered

### Approach 1: Extend hand-rolled provider + inline script + localStorage
**Selected:** YES
**Rationale:** Respects the existing `ThemeProvider.tsx` named in the request, no runtime dependency, full control, standard FOUC primitive (render-blocking head script). Cost: the hydration/validation edge cases must be handled by hand (addressed in this plan).

### Approach 2: Adopt `next-themes`
**Selected:** NO
**Rationale:** Battle-tested; persistence, OS preference, and flash-prevention come free (~2 KB). Rejected as the default because it **replaces** the file the request points to and adds a dependency for a binary toggle. Reconsider if "system" mode or multi-theme support becomes a near-term requirement (Eric S2 / Wigsy POSITIVE both note hand-rolling is appropriate at this scope).

### Approach 3: Hand-rolled provider + cookie-based SSR  ← reviewer-recommended alternative
**Selected:** NO (defaulted away because the approach question was dismissed)
**Rationale:** Eric (architecture, S1) recommends this strongly: the server reads the theme cookie via `cookies()` and renders `<html class={...}>` correct on the first byte — **no inline script, no `suppressHydrationWarning`, no FOUC, and no hydration mismatch by construction** (dissolves critical items C2/C3 and concern N2 at once). `ThemeToggle` receives the server-resolved value as a prop so `aria-checked` is correct at SSR. Trade-off: the cookie ships on every request (a few bytes) and reading it makes the layout dynamic (loses static optimization — negligible for an app shell). **If you prefer correctness-by-construction over keeping the server stateless about theme, switch Decision 1 to this approach.** It is the idiomatic App Router pattern.

> Approach comparison matrix is in the appendix.

## Implementation Plan

> **Sequencing note (Eric S4):** phases are ordered so every phase produces something openable in a browser. Scaffold → layout+tokens (see the page render) → provider (apply theme) → toggle (interact). The single hardest property — *no flash on reload* — can only be validated against a **production build**, so verification uses `next build && next start`, not just dev.

### Phase 0: Project scaffold (prerequisite)

**Goal:** Make the app buildable, runnable, type-checkable, and testable. Without this, no later phase can be verified.

**Estimated Effort:** Medium

**Dependencies:** None

**Files to Create:**
- `web/package.json`: pin `next`, `react`, `react-dom`, `typescript`, `@types/react`, `@types/react-dom`, `@types/node`; dev: `vitest`, `@testing-library/react`, `@testing-library/jest-dom`, `@testing-library/user-event`, `jsdom`. Scripts: `dev`, `build`, `start`, `test`.
- `web/next.config.mjs`: minimal config.
- `web/tsconfig.json`: `strict: true`; `paths` alias `"@/*": ["./*"]` with `baseUrl: "."` (so imports resolve from `web/`).
- `web/next-env.d.ts`.
- `web/vitest.config.ts` + `web/vitest.setup.ts`: jsdom environment, `@testing-library/jest-dom` matchers, `@/` alias mirrored for tests.

**Files to Modify:** None
**Files to Delete:** None
**Code to Remove:** None
**Database Changes:** None

**Implementation Details:** App root is `web/`. Use the `@/` path alias for intra-app imports. Confirm `npm install` resolves and `next build` succeeds against the (still empty) app before proceeding — note that Phase 0 alone won't build until Phase 1's `layout.tsx` exists, so validate Phase 0 jointly with Phase 1.

**Verification:** `npm install` clean; `npx tsc --noEmit` runs; `npx vitest run` discovers zero tests without error.

---

### Phase 1: Root layout + anti-flash script + token layer

**Goal:** Wire `ThemeProvider` into the app, prevent the flash on reload, and give the app visible theme-driven colors.

**Estimated Effort:** Medium

**Dependencies:** Phase 0

**Files to Create:**
- `web/app/layout.tsx` (**server** component):
  - `<html lang="en" suppressHydrationWarning>` — `suppressHydrationWarning` is required because the inline script mutates the class before hydration (it is scoped to `<html>` only; descendants are handled in Phase 3 via a `mounted` gate).
  - In `<head>`, a render-blocking script set with `dangerouslySetInnerHTML={{ __html: THEME_SCRIPT }}` where `THEME_SCRIPT` is a **static string literal with zero interpolation** (Wigsy C1 / Eric N2). The script: `try { if (localStorage.getItem("theme") === "dark") document.documentElement.classList.add("dark"); } catch (e) {}`. It adds **only** the fixed `"dark"` literal and only when the stored value is **exactly** `"dark"` (allowlist — Wigsy C2), and its read is wrapped in try/catch so storage exceptions can't blank the page (Wigsy W2).
  - `<body>` wraps `{children}` in `<ThemeProvider>`.
  - `import "./globals.css";`
- `web/app/globals.css`:
  - `:root { color-scheme: light; --bg:#fff; --fg:#111; --muted:#555; --accent:#2563eb; }`
  - `.dark { color-scheme: dark; --bg:#0b0e14; --fg:#e6e6e6; --muted:#9aa0a6; --accent:#60a5fa; }` — `color-scheme` per theme so native controls/scrollbars follow (Eric N5 / Wigsy W5).
  - `html { background: var(--bg); }` (background on `html`, not only `body`, so overscroll areas match — Eric N5) and `body { background: var(--bg); color: var(--fg); margin:0; font-family: system-ui, sans-serif; transition: background-color .2s ease, color .2s ease; }`.
  - `.settings { max-width: 40rem; margin: 0 auto; padding: 2rem; }` plus switch styles with a visible `:focus-visible` outline (Wigsy S1).

**Files to Modify:** None
**Files to Delete:** None
**Code to Remove:** None

**Implementation Details:** Use a **single theme signal — the `.dark` class** (drop `data-theme` to avoid two signals that can disagree — Wigsy S4). The `localStorage` key (`"theme"`) and class (`"dark"`) literals are unavoidably duplicated between this stringified script and the provider module; leave a `// COUPLING: keep "theme"/"dark" in sync with ThemeProvider + globals.css` comment at the script (Eric N1 / Wigsy S3).

**Verification:** `next build && next start`; load any route — body reflects token colors; with `localStorage.theme="dark"` preset, a hard reload paints dark **with no flash** of light.

---

### Phase 2: Theme core — extend `ThemeProvider.tsx`

**Goal:** Turn the provider into a real, persisted, single-source theme controller.

**Estimated Effort:** Medium

**Dependencies:** Phase 1 (so DOM application has the layout + tokens to act on)

**Files to Modify:**
- `web/components/ThemeProvider.tsx`:
  - `export type Theme = "light" | "dark";` Export the literals `THEME_STORAGE_KEY = "theme"` and `DARK_CLASS = "dark"` so all module-side usages reference one source (Eric N1 / Wigsy S3).
  - Context value becomes `{ theme: Theme; toggleTheme: () => void }` — **no `setTheme`** (a binary control only needs toggle; `setTheme` is speculative — Wigsy W4).
  - `createContext<ThemeContextValue | undefined>(undefined)`; `useTheme()` throws if used outside the provider (fail-loud — Eric N4).
  - **Lazy initializer** `useState<Theme>(readStoredTheme)` where `readStoredTheme()` guards `typeof window === "undefined"` → `"light"`, else `try { return localStorage.getItem(THEME_STORAGE_KEY) === "dark" ? "dark" : "light"; } catch { return "light"; }`. This reads the **same key + allowlist** the inline script used, so client state agrees with the pre-painted DOM (fixes Eric C2 / Wigsy C3). Anything but exactly `"dark"` collapses to light (Wigsy C2).
  - **Single DOM-application effect** keyed on `theme`: `useEffect(() => { document.documentElement.classList.toggle(DARK_CLASS, theme === "dark"); try { localStorage.setItem(THEME_STORAGE_KEY, theme); } catch {} }, [theme])`. Setters stay pure state updates; the DOM is mutated in exactly one place (Eric N3). Write failure (quota/private mode) is swallowed — the UI still works for the session (Wigsy W2).
  - `toggleTheme = () => setTheme(t => t === "dark" ? "light" : "dark")`.
  - `useTheme` now returns the object — a **breaking** change to the hook signature, safe because it is imported nowhere (verified by both reviewers). Land it atomically with its first consumer (Phase 3) and note the signature change in the commit body (Wigsy W3).

**Files to Delete:** None
**Code to Remove:** The discarded `useState` setter pattern and the `Theme = "light"`-only type in the current file (replaced wholesale).

**Implementation Details:** The provider renders no theme-dependent markup itself, so its lazy-init to `"dark"` on the client does not by itself cause a hydration mismatch; the only theme-dependent descendant is `ThemeToggle`, isolated in Phase 3.

**Verification:** Unit tests in Phase 4; manually, toggling updates the `.dark` class on `<html>` and persists across reload.

---

### Phase 3: Settings UI — the accessible switch

**Goal:** Render an accessible dark-mode switch on the settings page without a hydration mismatch.

**Estimated Effort:** Small

**Dependencies:** Phase 2

**Files to Create:**
- `web/components/ThemeToggle.tsx` (`"use client"`):
  - Uses `useTheme()`. A native `<button type="button" role="switch">` base element so keyboard (Space/Enter) and focus come for free (Wigsy S1).
  - A `mounted` flag (`const [mounted, setMounted] = useState(false); useEffect(() => setMounted(true), [])`). Render theme-independent markup until mounted, then reflect state: `aria-checked={mounted ? theme === "dark" : undefined}`, and keep the control inert (`disabled` or non-asserting) for the one pre-mount frame. This guarantees server HTML and the first client render match, eliminating the toggle-level hydration mismatch (Eric C3 / Wigsy C3).
  - Accessible name via a visible `<label>`/`aria-labelledby` to "Dark mode" (not icon-only — Wigsy S1). Visible focus indicator from `globals.css`.

**Files to Modify:**
- `web/app/settings/page.tsx`: stays a **server** component (correct boundary — Eric STRENGTH); remove the placeholder comment; render `<ThemeToggle />` inside `<section aria-label="Appearance">`.

**Files to Delete:** None
**Code to Remove:** The `{/* Theme toggle will live here. */}` placeholder comment and the self-closing empty `<section aria-label="Appearance" />`.

**Verification:** Phase 4 tests; manually, the switch is keyboard-operable, `aria-checked` tracks the theme after mount, and clicking flips the whole app.

---

## Testing Strategy

Test tooling is stood up in Phase 0 (Vitest + React Testing Library + jsdom) so "add tests" is real, not aspirational (Wigsy S2). Assert on actual DOM (`<html>` class, `aria-checked`), never on whether a mock was called.

### Unit Tests
- **`web/components/ThemeProvider.test.tsx`:**
  - `readStoredTheme` (or provider initial state) returns `"light"` for: missing key, `null`, garbage (`"DARK"`, `"dark x"`, `""`, a CSS-injection-looking string), and a thrown `SecurityError` (mock `localStorage.getItem` to throw). Returns `"dark"` **only** for exactly `"dark"`. (Directly tests Wigsy C2.)
  - `toggleTheme` flips `theme`, toggles the `.dark` class on `document.documentElement`, and writes `localStorage`.
  - A thrown `QuotaExceededError` on write is swallowed while in-memory state and the DOM class still update (Wigsy W2).
  - `useTheme()` outside a provider throws (Eric N4).
- **`web/components/ThemeToggle.test.tsx`:**
  - After mount, renders `role="switch"` with `aria-checked` matching the theme; toggles on **click** and on **keyboard** (Space/Enter); the accessible name is "Dark mode".

### Integration / Manual Tests
- **Persistence:** preset `localStorage.theme="dark"`, reload → app initializes dark; toggle to light, reload → stays light.
- **No-flash (production build only):** `next build && next start`; with dark preset, throttle CPU/network and hard-reload — first paint is dark, no light flash (Eric C1).
- **No hydration warnings:** load the settings page with React strict/dev; console shows no hydration mismatch on the toggle.

## Risks & Mitigations

### Risk 1: First-paint flicker / hydration mismatch for returning dark users
**Likelihood:** High (if unaddressed) · **Impact:** High
**Mitigation:** Provider lazy-inits from the same key+allowlist the inline script used; the toggle defers `aria-checked` behind a `mounted` gate. Verified by the no-hydration-warning manual test. **Rollback:** if mismatches persist, switch to Approach 3 (cookie SSR), which removes the mismatch by construction.

### Risk 2: App unbuildable / unverifiable (no scaffold)
**Likelihood:** Certain without Phase 0 · **Impact:** High
**Mitigation:** Phase 0 creates the scaffold; FOUC verified against a production build, not dev. **Rollback:** n/a (prerequisite).

### Risk 3: `dangerouslySetInnerHTML` XSS / CSP
**Likelihood:** Low · **Impact:** High if violated
**Mitigation:** Script body is a static literal with zero interpolation; it never writes a stored value into markup, only toggles a fixed class (Wigsy C1/C2). **Known future constraint (Wigsy W1):** a strict `script-src` CSP will need a per-request nonce on this tag (the body stays static; only the nonce attribute is dynamic) or `'unsafe-inline'`. Documented so a future CSP rollout doesn't silently break anti-flash.

### Risk 4: `localStorage` unavailable/throws (private mode, partitioned storage, quota)
**Likelihood:** Medium · **Impact:** Low
**Mitigation:** Every access (inline script read, provider mount read, provider write) is `typeof window`-guarded and try/catch-wrapped; failures fall back to light and are non-fatal/session-only (Wigsy W2).

### Risk 5: Coupling drift across the three theme literals
**Likelihood:** Medium · **Impact:** Medium (silent re-flash)
**Mitigation:** Module-side usages reference exported constants; the one unavoidable duplication (stringified inline script) carries a `COUPLING` comment naming its parallel sites (Eric N1 / Wigsy S3).

## Verification Steps

1. **Build & type-check:** `cd web && npm install && npx tsc --noEmit && npm run build` — clean.
2. **Unit tests:** `npx vitest run` — all pass, including the allowlist and quota-error cases.
3. **No-flash:** `npm run build && npm start`; preset dark; hard reload → no light flash.
4. **Persistence:** toggle, reload, confirm the choice sticks both directions.
5. **Hydration:** load settings in dev → no hydration warnings in console.
6. **Accessibility:** operate the switch with keyboard only; verify visible focus ring and that `aria-checked` tracks the theme.

## Success Criteria

- [ ] App builds (`next build`) and type-checks with no errors.
- [ ] A switch in `Settings → Appearance` flips the **whole app** between light and dark.
- [ ] The choice **persists across reloads** in both directions.
- [ ] **No flash** of the wrong theme on reload in a production build.
- [ ] **No hydration mismatch warnings** on the settings page.
- [ ] Switch is keyboard-operable with a visible focus indicator and an accessible name.
- [ ] Stored value is allowlisted (`"dark"` exactly, else light) in both the inline script and the provider.
- [ ] All unit tests pass, including garbage-value and storage-exception cases.
- [ ] No dead code: placeholder comment and empty section removed; no leftover `data-theme`/`setTheme` if unused.
- [ ] Code review passed.

## Assumptions

- The project is **Next.js App Router** with the app root at `web/` (inferred from `web/app/...`, `"use client"`, and the file paths). If the framework differs, Phase 0 and the layout/script mechanics must be revisited.
- **Binary** light/dark only; `prefers-color-scheme` is **not** honored on first visit in v1 (deferred decision — a fresh visitor sees light). Honoring the OS default on first load and a cross-tab `storage` listener are noted as cheap v2 enhancements (Eric S3 / Wigsy W5).
- A single `.dark` class is the only theme signal; `data-theme` is intentionally not used.
- No CSP is configured yet; if one is added later, see Risk 3.

**If any assumption is invalid, revisit this plan before implementation.**

## Review Feedback Addressed

### Critical Items
- **No Next scaffold (Eric C1):** added Phase 0; FOUC verified against a production build.
- **Init-to-light flicker / hydration mismatch (Eric C2/C3, Wigsy C3):** provider lazy-inits from the same key+allowlist as the inline script; toggle gates `aria-checked` behind a `mounted` flag.
- **Inline-script XSS (Wigsy C1, Eric N2):** static literal via `dangerouslySetInnerHTML`, zero interpolation, fixed class only.
- **Stored-value validation (Wigsy C2):** strict `"dark"`-only allowlist in both code paths; raw value never written to markup.
- **Storage exceptions (Wigsy W2):** try/catch on inline read, mount read, and writes; non-fatal write failure.

### Concerns
- **Constant coupling (Eric N1 / Wigsy S3):** exported constants module-side; `COUPLING` comment on the stringified script.
- **DOM application spread across setters (Eric N3):** centralized in one `theme`-keyed effect; setters pure.
- **API over-surface (Wigsy W4):** trimmed to `{ theme, toggleTheme }`.
- **Context default (Eric N4):** `undefined` default; `useTheme` throws outside provider.
- **Viewport/native-control theming (Eric N5 / Wigsy W5):** background on `html`; `color-scheme` per theme.
- **Two theme signals (Wigsy S4):** `.dark` class only.

### Suggestions Incorporated
- Native `<button>` switch base, real accessible name, visible focus ring (Wigsy S1).
- Phase reordering for browser-verifiable increments (Eric S4).
- Test tooling stood up in Phase 0 with non-superficial cases (Wigsy S2).
- Cookie-based SSR recorded as the flagged reviewer-recommended alternative (Eric S1).

---

## APPENDIX: Detailed Exploration Findings

### Files Investigated
- `web/components/ThemeProvider.tsx` — client provider; `Theme = "light"` only, bare-string context, discarded setter, no persistence/DOM application, `useTheme` returns a string. Imported nowhere.
- `web/app/settings/page.tsx` — server component; placeholder `<section aria-label="Appearance" />` + comment; `className="settings"` with no CSS.
- Repo root — no `package.json`, `next.config.*`, `tsconfig.json`, `globals.css`, or `layout.tsx`.

### Execution Flow
There is no running app today: no layout mounts the provider, the provider exposes no way to change the theme, and nothing persists or applies a theme to the DOM. The feature is built largely greenfield within the conventions the two stub files establish.

### Test Coverage
None — no test runner present. Tooling added in Phase 0.

### Recent Changes
Single commit `841ea07 baseline`.

### Dead Code & Cruft
- `web/app/settings/page.tsx`: the `{/* Theme toggle will live here. */}` placeholder comment and the empty self-closing `<section>` (resolved in Phase 3).
- `web/components/ThemeProvider.tsx`: the discarded `useState` setter and light-only `Theme` type (replaced in Phase 2).

---

## APPENDIX: Approach Analysis

### Approach Comparison Matrix

| Criteria | A1: localStorage + script (selected) | A2: next-themes | A3: cookie SSR (reviewer-rec.) |
|---|---|---|---|
| New dependency | No | Yes (~2 KB) | No |
| Keeps existing `ThemeProvider.tsx` | Yes (extends) | No (replaces) | Yes (extends) |
| Flash on reload | None (via script) | None | None (by construction) |
| Hydration-mismatch risk | Medium — needs lazy-init + `mounted` gate | Low | None by construction |
| OS-preference support | Manual (deferred) | Free | Manual |
| Static optimization | Preserved | Preserved | Layout becomes dynamic |
| Implementation complexity | Medium | Low | Medium |

### Selection Rationale
A1 is the default because it honors the existing file named in the request and adds no dependency, with all hydration/validation edge cases explicitly handled in this plan. A3 is the reviewer-recommended alternative and is strictly cleaner on the hydration axis — switch Decision 1 to A3 if correctness-by-construction is preferred over keeping the server stateless about theme. A2 becomes attractive if "system" mode or multi-theme support is wanted near-term.

---

**This plan is ready for implementation. To execute:**
```bash
/implement-plan
```
