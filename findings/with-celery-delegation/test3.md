# Load Test Result — Celery + Redis (Async Send)

**Config:** Django (Gunicorn) → Postgres write + Redis enqueue → response returned → Celery worker processes send async
**Concurrency:** 100 users, spawn rate 2
**Endpoint:** `POST /api/v1/notifications/send/`
**Host:** http://localhost:8000

## Locust Results

| Type | Name | # Requests | # Fails | Median (ms) | 95%ile (ms) | 99%ile (ms) | Average (ms) | Min (ms) | Max (ms) | Avg size (bytes) | Current RPS | Current Failures/s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| POST | /api/v1/notifications/send/ | 2221 | 0 | 82 | 240 | 310 | 115.4 | 73 | 425 | 29 | 47.5 | 0 |
| **Aggregated** | | 2221 | 0 | 82 | 240 | 310 | 115.4 | 73 | 425 | 29 | 47.5 | 0 |

**RPS:** 31.42
**Failure rate:** 0%

## Notes
- Median held steady at 82ms (same as 50-user run); 95th/99th percentile roughly flat too (240/310 vs 230/320) — API-layer response time is NOT degrading meaningfully with concurrency, because the view no longer waits on the actual send.
- RPS scaled from 18.63 (50 users) → 31.42 (100 users) — sub-linear growth (not a full 2x), suggesting some contention starting to appear at the API/DB layer even though it's not showing up as request failures.
- Real bottleneck has now moved downstream: Celery queue backlog observed at ~900-1000 unprocessed messages in Redis during/after the run, confirming task consumption throughput is far below request-acceptance throughput. This is expected — Celery worker concurrency (likely default ~= CPU core count) can't keep pace with 100 concurrent requests each enqueuing a task with a simulated 1-2s processing time.
- One connection reset (`ConnectionResetError`, errno 54) was observed during the 50-user run — same error previously seen on WSL2 (errno 104) and attributed there to a WSL2 networking artifact. Recurrence on native macOS at higher concurrency means that conclusion needs revisiting — likely Gunicorn worker pool or Postgres connection pool exhaustion under concurrent load, not WSL2-specific. Flagged for follow-up.

## Key takeaway
RPS at the API layer is now decoupled from actual notification delivery throughput — Django's job is just "persist + enqueue," so response times stay flat under load. The bottleneck has shifted entirely to Celery worker capacity (how many tasks can be processed in parallel), not Gunicorn/API capacity. Next lever to pull: Celery worker concurrency/count, to close the gap between request-acceptance rate and task-processing rate.