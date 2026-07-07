## Run 8 — Gunicorn, sync workers, 12 workers, 50 users (with psycopg3 pooling)

**Date:** 2026-06-25

**Config:**
- Server: Gunicorn, `sync` worker class, **12 workers** (up from 4; machine has 8 cores)
- DB: PostgreSQL (WSL2), psycopg3 native connection pooling (min_size=2, max_size=20)
- Locust users: 50
- Endpoint: `POST /api/v1/notifications/send/`

**Results:**

| Metric | Value |
|---|---|
| Total Requests | 207 |
| Failures | 0 (0%) |
| RPS | 4.34 |
| Median (ms) | 5900 |
| 95%ile (ms) | 10000 |
| 99%ile (ms) | 10000 |
| Average (ms) | 5674.26 |
| Min (ms) | 620 |
| Max (ms) | 10960 |
| Avg response size (bytes) | 143.25 |

**Comparison vs. Run 1 (4 workers, 50 users)**

| Metric | Run 1 (4 workers) | Run 8 (12 workers) |
|---|---:|---:|
| RPS | 2.13 | 4.34 |
| Median | 20000 ms | 5900 ms |
| 95%ile | 21000 ms | 10000 ms |
| Min | 1772 ms | 620 ms |
| Max | 21693 ms | 10960 ms |
| Failures | 0% | 0% |

**Observations:**
- Tripling workers (4 → 12) roughly **doubled RPS** (2.13 → 4.34) and cut median latency by **~70%** (20000ms → 5900ms) — a real, substantial improvement, though not a clean linear 3x scale-up.
- Min latency also dropped well below the Run 6 single-request baseline of ~1.2s (620ms here) — suggests some requests are now landing on a freshly-idle worker with near-zero queue wait, consistent with much more parallel capacity relative to 50 concurrent users.
- This was tested at 50 users, not 100 (deviating from the 10/50/100 methodology) — noting for consistency in future comparisons.

**Hypothesis:**
- More workers does help meaningfully, supporting the queueing theory from Run 6/7 — sync workers were the bottleneck, not the DB or pool layer (already resolved). At 12 workers, there's enough parallel capacity that 50 concurrent users no longer overwhelm the queue the way they did at 4 workers.
- Still open: how this holds at 100 users (next logical test, per the 10/50/100 cadence), and whether throughput is starting to plateau as workers approach the `(2×cores)+1 ≈ 17` heuristic ceiling, or if there's still room to climb before diminishing returns set in.

---
