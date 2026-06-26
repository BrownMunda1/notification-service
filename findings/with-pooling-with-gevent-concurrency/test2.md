## Run 10 — Gunicorn, gevent workers, 4 workers, 50 users (with psycopg3 pooling)

**Date:** 2026-06-26

**Config:**
- Server: Gunicorn, `gevent` worker class (first test), 4 workers
- DB: PostgreSQL (WSL2), psycopg3 native connection pooling (min_size=2, max_size=20)
- Locust users: 50
- Endpoint: `POST /api/v1/notifications/send/`

**Results:**

| Metric | Value |
|---|---|
| Total Requests | 181 |
| Failures | 23 (13%) |
| RPS | 3.95 |
| Median (ms) | 4300 |
| 95%ile (ms) | 14000 |
| 99%ile (ms) | 18000 |
| Average (ms) | 5751.29 |
| Min (ms) | 45 |
| Max (ms) | 17904 |
| Avg response size (bytes) | 126.07 |

**Observations:**
- First run with actual failures since pooling was introduced (13%) — a regression compared to every sync-worker run so far (all 0% failures).
- Min latency dropped dramatically (45ms vs ~600-700ms range in sync runs) — strong sign gevent is working as intended: many requests are now genuinely concurrent within a single worker process instead of queueing one-by-one.
- Median (4300ms) and RPS (3.95) are competitive with the 12-worker sync result (Run 8: 5900ms median, 4.34 RPS) — but with only 4 *processes* this time, not 12.
- Failures appearing with otherwise "clean" application logs is suspicious — points toward a DB connection pool issue specifically, since `gevent` lets one worker hold *many more concurrent in-flight requests* than the psycopg3 pool's `max_size=20` was sized for. With 50 users now genuinely concurrent (not queued one at a time), the existing pool ceiling of 20 connections may be getting exceeded, and pool timeout errors are likely landing in Gunicorn's error log or surfacing as a Locust-side exception, not necessarily in Django's app-level logs.

**Hypothesis:**
- Likely cause: `psycopg_pool.PoolTimeout` (same failure signature seen back in Run 5 on `runserver`) — except this time triggered by gevent's much higher real concurrency overwhelming a pool sized for the old sync-worker queueing model, rather than by slow per-request hold times. Need to check Gunicorn's stderr/error log directly and Locust's per-request exception/error column (not just Django's app logger) to confirm.
- Next step: inspect actual error type, then consider raising `max_size` on the psycopg3 pool to match gevent's higher concurrency ceiling before re-testing.

---
