# Load Test Result — Celery + Redis (Async Send)

**Config:** Django (Gunicorn) → Postgres write + Redis enqueue → response returned → Celery worker processes send async
**Concurrency:** 50 users, spawn rate 2
**Endpoint:** `POST /api/v1/notifications/send/`
**Host:** http://localhost:8000

## Locust Results

| Type | Name | # Requests | # Fails | Median (ms) | 95%ile (ms) | 99%ile (ms) | Average (ms) | Min (ms) | Max (ms) | Avg size (bytes) | Current RPS | Current Failures/s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| POST | /api/v1/notifications/send/ | 1044 | 1 | 82 | 230 | 320 | 118.78 | 0 | 382 | 28.61 | 23.1 | 0 |
| **Aggregated** | | 1044 | 1 | 82 | 230 | 320 | 118.78 | 0 | 382 | 28.61 | 23.1 | 0 |

**RPS:** 18.63
**Failure rate:** 0% (1 fail out of 1044 requests)

## Notes
- Median actually dropped slightly vs 10-user run (94ms → 82ms), 95th/99th percentile rose a bit (180→230, 250→320) — some tail latency creeping in under more concurrent load, likely early sign of contention (Postgres connections, Gunicorn worker pool, or Redis enqueue contention) even though it's still healthy overall.
- 1 failure recorded — worth checking Locust's failure log / Django logs to identify cause before assuming it's noise.
- RPS scaled roughly 4x going from 10→50 users (4.56 → 18.63), consistent with more concurrent throughput rather than a hard bottleneck yet.