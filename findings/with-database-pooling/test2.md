## Run 4 — 50 users, with Django native connection pooling (psycopg3 pool, min_size=2, max_size=20)

**Date:** 2026-06-21
**Config:** 50 users, spawn rate 2/s. Same as Run 2, but with DB connection pooling now enabled in `settings.py` (previously `CONN_MAX_AGE=0`, no pooling).
**Endpoint under test:** `POST /api/v1/notifications/send/`
**Server:** `manage.py runserver` (still the dev server — only the DB layer changed)

| Type | Name | # Requests | # Fails | Median (ms) | 95%ile (ms) | 99%ile (ms) | Average (ms) | Min (ms) | Max (ms) | Avg size (bytes) | Current RPS | Current Failures/s |
|------|------|-----------:|--------:|------------:|------------:|------------:|-------------:|---------:|---------:|------------------:|------------:|--------------------:|
| POST | /api/v1/notifications/send/ | 181 | 0 | 17000 | 24000 | 25000 | 15143.23 | 2084 | 25029 | 143.45 | 2.1 | 0 |
| **Aggregated** | | 181 | 0 | 17000 | 24000 | 25000 | 15143.23 | 2084 | 25029 | 143.45 | 2.1 | 0 |

### Comparison vs. Run 2 (50 users, no pooling)

| Metric | Run 2 (no pooling) | Run 4 (with pooling) |
|---|---:|---:|
| Median latency | 22000 ms | 17000 ms |
| 95%ile latency | 29000 ms | 24000 ms |
| RPS | 1.7 | 2.1 |
| Failures | 0% | 0% |

### Observations
- Latency improved (~23% lower median) and RPS ticked up slightly — connection pooling is helping, but only modestly at 50 users.
- Failures were already 0% at 50 users even *before* pooling, so this run doesn't yet prove pooling fixes the failure problem — that only showed up at 100 users (Run 3, 13% failures from exhausted Postgres connections).
- The bulk of the latency is still clearly coming from somewhere else — most likely the same single-threaded dev server queueing identified earlier. Pooling fixes *connection exhaustion*, not *request queueing* — these are two separate bottlenecks stacked on top of each other.

### Next step
Re-run at 100 users (same as Run 3) with pooling now enabled, to directly test whether the connection-exhaustion failures (13% in Run 3) disappear. This isolates pooling's effect on the *failure* problem specifically, separate from the *latency* problem which likely still needs Gunicorn to address.
