We want a "saved filters" feature on the dashboard: a user can save their current set of filters
under a name, and re-apply a saved set later from a dropdown. Saved filters need to follow the user
across devices — if they save a filter on their laptop it should be there on their phone, so it
can't just live in the browser.

Please plan this out. The backend is Go (api/handlers, api/store, Postgres migrations) and the UI is
React (web/components/FilterBar.tsx, web/lib/api.ts).
