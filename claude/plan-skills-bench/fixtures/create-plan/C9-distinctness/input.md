Add real full-text search to our notes app. Right now "search" only does a substring match on the
note title; we want it to search the full note body too and rank results sensibly (best matches
first). Scale matters: power users have ~50k notes each and search latency needs to stay snappy.

Please plan this out. Backend is Python over Postgres — store.py, models.py, and the migrations
directory.
