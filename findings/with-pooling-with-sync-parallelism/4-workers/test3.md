## Run 7 — Gunicorn, sync workers, 4 workers, 100 users (with psycopg3 pooling)

**Date:** 2026-06-25

**Config:**
- Server: Gunicorn, `sync` worker class, 4 workers
- DB: PostgreSQL (WSL2), psycopg3 native connection pooling (min_size=2, max_size=20)
- Locust users: 100
- Endpoint: `POST /api/v1/notifications/send/`

**Results:**

| Metric | Value |
|---|---|
| Total Requests | 254 |
| Failures | 0 (0%) |
| RPS | 3.62 |
| Median (ms) | 11000 |
| 95%ile (ms) | 22000 |
| 99%ile (ms) | 24000 |
| Average (ms) | 10825.15 |
| Min (ms) | 714 |
| Max (ms) | 24968 |
| Avg response size (bytes) | 143.46 |

**Comparison vs. Run 5 (`runserver`, pooling, 100 users — from prior session)**

| Metric | Run 5 (`runserver`, pooling) | Run 7 (Gunicorn, 4 sync workers, pooling) |
|---|---:|---:|
| RPS | 3.2 | 3.62 |
| Failures | 6% (`psycopg_pool.PoolTimeout`) | 0% |
| Median | 26000 ms | 11000 ms |
| 95%ile | 58000 ms | 22000 ms |
| Min | 2019 ms | 714 ms |
| Max | 61409 ms | 24968 ms |

**Observations:**
- **Failures dropped from 6% to 0%** — confirms Run 5's hypothesis: the pool was timing out on `runserver` because slow single-process request handling held connections too long. Gunicorn's multi-process model frees connections faster, so the pool never saturates long enough to time out.
- **Median more than halved** (26000ms → 11000ms) and **max latency dropped** (61409ms → 24968ms) — the long-tail "stuck" requests are gone.
- **RPS barely moved** (3.2 → 3.62), despite fixing both the failure mode and cutting latency significantly. This lines up with the Run 6 baseline: 4 sync workers × ~1.2s/request ≈ 3.3 RPS theoretical ceiling — we're already close to it.

**Hypothesis:**
- Connection pool exhaustion and `runserver`'s single-process bottleneck are now both resolved. The remaining ceiling is **sync worker queueing**: only 4 requests processed at a time, everyone else waits in line, regardless of how fast the DB itself responds.
- Two distinct paths forward: (a) add more sync workers (bounded by `(2×cores)+1` ≈ 17 on this 8-core machine) to increase parallel capacity, or (b) switch to `gevent`/`eventlet` worker class to get many more concurrent in-flight requests per worker by yielding during I/O wait — relevant since the 1.2s baseline likely includes meaningful I/O wait time (DB), not pure CPU work.
- Still unresolved and separate from worker concurrency: why a single isolated request takes ~1.2s in the first place (Run 6 baseline) — worth profiling the view/serializer/DB query directly.

---
