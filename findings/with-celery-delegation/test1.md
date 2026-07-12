# Load Test Result — Celery + Redis (Async Send)

**Config:** Django (Gunicorn) → Postgres write + Redis enqueue → response returned → Celery worker processes send async
**Concurrency:** 10 users, spawn rate 2
**Endpoint:** `POST /api/v1/notifications/send/`
**Host:** http://localhost:8000

## Locust Results

| Type | Name | # Requests | # Fails | Median (ms) | 95%ile (ms) | 99%ile (ms) | Average (ms) | Min (ms) | Max (ms) | Avg size (bytes) | Current RPS | Current Failures/s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| POST | /api/v1/notifications/send/ | 135 | 0 | 94 | 180 | 250 | 106.06 | 73 | 251 | 28 | 4.9 | 0 |
| **Aggregated** | | 135 | 0 | 94 | 180 | 250 | 106.06 | 73 | 251 | 28 | 4.9 | 0 |

**RPS:** 4.56
**Failure rate:** 0%

## Notes
- To compare against: prior synchronous baseline (pre-Celery) at 10 users.
- Response time here reflects only DB write + Redis enqueue — actual "send" work now happens out-of-band in the Celery worker.