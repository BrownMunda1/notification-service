## Run 1 — Baseline (Django dev server, `manage.py runserver`)

**Config:** 10 users, spawn rate 2/s, no run-time limit (manual stop)
**Endpoint under test:** `POST /api/v1/notifications/send/`
**Server:** `manage.py runserver` (single-threaded dev server)

| Type | Name | # Requests | # Fails | Median (ms) | 95%ile (ms) | 99%ile (ms) | Average (ms) | Min (ms) | Max (ms) | Avg size (bytes) | Current RPS | Current Failures/s |
|------|------|-----------:|--------:|------------:|------------:|------------:|-------------:|---------:|---------:|------------------:|------------:|--------------------:|
| POST | /api/v1/notifications/send/ | 90 | 0 | 3300 | 5200 | 5600 | 3424.04 | 1961 | 5639 | 142.37 | 2.1 | 0 |
| **Aggregated** | | 90 | 0 | 3300 | 5200 | 5600 | 3424.04 | 1961 | 5639 | 142.37 | 2.1 | 0 |

### Observations
- Only 10 concurrent users produced a median response time of **3.3 seconds** — far too slow for what should be a simple DB write.
- No failures (0%) — the server isn't rejecting/erroring requests, it's just queueing them.
- Current RPS sitting at ~2.1 with only 10 users suggests the server is processing requests largely one at a time.

### Hypothesis (to verify in next run)
This is consistent with `manage.py runserver` being single-threaded — requests are likely queuing up behind each other rather than being processed concurrently. Next step: re-run with more users to see if RPS plateaus (confirming the bottleneck) before switching to a production-grade server (gunicorn) to compare.
