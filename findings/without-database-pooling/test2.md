## Run 2 — 50 users (Django dev server, `manage.py runserver`)

**Date:** 2026-06-21
**Config:** 50 users, spawn rate 2/s (only user count changed vs. Run 1, to isolate the variable)
**Endpoint under test:** `POST /api/v1/notifications/send/`
**Server:** `manage.py runserver` (single-threaded dev server)

| Type | Name | # Requests | # Fails | Median (ms) | 95%ile (ms) | 99%ile (ms) | Average (ms) | Min (ms) | Max (ms) | Avg size (bytes) | Current RPS | Current Failures/s |
|------|------|-----------:|--------:|------------:|------------:|------------:|-------------:|---------:|---------:|------------------:|------------:|--------------------:|
| POST | /api/v1/notifications/send/ | 176 | 0 | 22000 | 29000 | 29000 | 21224.17 | 5769 | 32032 | 143.34 | 1.7 | 0 |
| **Aggregated** | | 176 | 0 | 22000 | 29000 | 29000 | 21224.17 | 5769 | 32032 | 143.34 | 1.7 | 0 |

### Observations
- **RPS did NOT increase** with 5x the users (1.63-1.7, vs. 2.1 in Run 1) — actually slightly *lower*. This confirms a hard throughput ceiling, not a temporary slowdown.
- **Median response time exploded from 3.3s → 22s** (a ~6.7x increase) for a 5x increase in concurrent users — classic queueing behavior, not processing getting slower per request.
- Still 0% failures — the dev server isn't erroring, it's just serializing every request through one thread, so the queue keeps growing.
- Max response time hit 32 seconds — some unlucky requests waited almost the entire test duration before being served.

### Conclusion
This is the textbook signature of a single-threaded server under concurrent load: **throughput plateaus while latency balloons linearly (or worse) with added concurrency**. The bottleneck is the dev server's request-handling model, not the database or notification logic.

### Next step
Switch from `manage.py runserver` to a production-grade WSGI server (e.g. Gunicorn with multiple workers) and re-run the same test (50 users, spawn rate 2) to see if RPS climbs and latency drops — isolating whether the server process model was indeed the bottleneck.
