# Answer key — C9

```yaml
scenario_id:        C9
skill:              create-plan
mode_expected:      FEATURE
agents_required:    [shane, dan]
expected_gate:      proceed
true_primary:       "Postgres full-text search: a tsvector over (title, body) with a GIN index and ts_rank ranking — fits the 50k-notes / low-latency constraint without standing up external infrastructure."
true_primary_locus: "new: migration adding a tsvector column + GIN index; store.search_notes rewritten to use @@ and ts_rank"
distinct_approaches_expected:
  - "Naive ILIKE on title+body (no ranking, sequential scan, too slow at 50k)."
  - "Postgres full-text search (tsvector + GIN + ts_rank)."
  - "External search engine / dedicated index service (most powerful, most operational overhead)."
padding_to_penalize:
  - "Three variants of LIKE (title-only / title+body / case-insensitive) presented as distinct approaches."
checkpoint_expected: fires
checkpoint_required_forks:
  - "Postgres FTS vs external engine (depends on the scale ceiling and roadmap)."
  - "Search scope: title only vs full body (the request says body — confirm)."
required_artifacts:
  - ">=3 distinct approaches"
  - "a comparison matrix across approaches"
```

## Notes

- `distinctness` is the headline dimension: the three approaches must differ mechanistically
  (substring scan vs in-database inverted index vs external index service). LIKE-variants score 1.
- `correct_primary`: `matches_answer_key` true iff the recommendation is Postgres full-text search.
  Recommending naive LIKE (ignores the scale/latency constraint) or an external engine for v1
  (over-engineered for the stated scale) is weaker and should be justified if chosen.
- Given the scripted answers (Postgres FTS, full body), the plan should commit to the tsvector+GIN
  approach over the full note body.
