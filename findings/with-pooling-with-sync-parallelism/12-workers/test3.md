## Run 9 — Gunicorn, sync workers, 12 workers, 100 users (with psycopg3 pooling)

**Date:** 2026-06-25

**Config:**
- Server: Gunicorn, `sync` worker class, 12 workers
- DB: PostgreSQL (WSL2), psycopg3 native connection pooling (min_size=2, max_size=20)
- Locust users: 100
- Endpoint: `POST /api/v1/notifications/send/`
- Note: total request count (462) is notably higher than Run 7's 254 — not a perfectly matched run duration/request count, factor in when comparing.

**Results:**

| Metric | Value |
|---|---|
| Total Requests | 462 |
| Failures | 0 (0%) |
| RPS | 4.18 |
| Median (ms) | 17000 |
| 95%ile (ms) | 23000 |
| 99%ile (ms) | 23000 |
| Average (ms) | 14533.34 |
| Min (ms) | 576 |
| Max (ms) | 23423 |
| Avg response size (bytes) | 144.01 |

**Comparison vs. Run 7 (4 workers, 100 users) and Run 8 (12 workers, 50 users)**

| Metric | Run 7 (4 workers, 100 users) | Run 8 (12 workers, 50 users) | Run 9 (12 workers, 100 users) |
|---|---:|---:|---:|
| RPS | 3.62 | 4.34 | 4.18 |
| Median | 11000 ms | 5900 ms | 17000 ms |
| 95%ile | 22000 ms | 10000 ms | 23000 ms |
| Min | 714 ms | 620 ms | 576 ms |
| Max | 24968 ms | 10960 ms | 23423 ms |
| Failures | 0% | 0% | 0% |

**Observations:**
- Going from 4→12 workers at the *same* 100-user load only modestly improved RPS (3.62 → 4.18) and actually made median latency **worse**, not better (11000ms → 17000ms) — the opposite direction from the 50-user comparison (Run 1 → Run 8), where 12 workers clearly helped.
- This lines up with the math worked through earlier: 100 concurrent users need roughly 100 workers to avoid queueing with sync workers. 12 workers is still far short of that for 100 users — you're just less far short than 4 workers was, so some improvement shows, but the queue still grows over the test duration the same way it did before.
- Min latency (576ms) is below even the Run 6 baseline (1122ms) — likely just an early request in the test landing on an idle worker before the queue built up, not a sign the bottleneck is resolved.

**Hypothesis:**
- Confirms the earlier conclusion: sync worker count needs to roughly match concurrent user count to avoid queueing growth. 12 workers is a reasonable middle ground for ~50 concurrent users but clearly insufficient for 100 — climbing worker count further would need to approach 100 to flatten latency at this load, which starts oversubscribing an 8-core machine and trading queueing delay for CPU context-switching overhead instead.
- This is the natural motivation for moving to `gevent`/`eventlet` workers (or async) next: handle many concurrent in-flight requests per OS process instead of needing one process per concurrent request — without requiring CPU core count to scale 1:1 with user count.

---
