## Run 3 — 100 users (Django dev server, `manage.py runserver`)

**Date:** 2026-06-21
**Config:** 100 users, spawn rate 2/s (only user count changed vs. Runs 1-2)
**Endpoint under test:** `POST /api/v1/notifications/send/`
**Server:** `manage.py runserver` (single-threaded dev server)

| Type | Name | # Requests | # Fails | Median (ms) | 95%ile (ms) | 99%ile (ms) | Average (ms) | Min (ms) | Max (ms) | Avg size (bytes) | Current RPS | Current Failures/s |
|------|------|-----------:|--------:|------------:|------------:|------------:|-------------:|---------:|---------:|------------------:|------------:|--------------------:|
| POST | /api/v1/notifications/send/ | 230 | 29 | 47000 | 59000 | 60000 | 38696.80 | 4226 | 60640 | 34727.07 | 2.8 | 0.2 |
| **Aggregated** | | 230 | 29 | 47000 | 59000 | 60000 | 38696.80 | 4226 | 60640 | 34727.07 | 2.8 | 0.2 |

### Observations
- **First failures appear: 13% failure rate** (29 out of 230 requests) — this is the breaking point. At 10 and 50 users the server was slow but reliable (0% failures); at 100 it starts actively failing.
- **Median latency 47s, max 60.6s** — requests are now waiting roughly a minute to complete, suggesting many are hitting a timeout ceiling around 60s (likely Locust's or the connection's default timeout) rather than ever truly being served.
- **RPS is roughly flat to slightly up (1.62 avg / 2.8 current)** vs. Run 2 — the ceiling is holding, not improving, even under far more pressure.
- **Average response size jumped drastically (143 bytes → 34,727 bytes)** — this is a strong hint that the failing responses aren't small JSON error messages, but something like a full HTML error/timeout page being returned instead of your API's normal JSON response. Worth inspecting what those 29 failed responses actually contain.

### Conclusion
100 concurrent users pushed the single-threaded dev server past its breaking point: queueing alone (seen in Runs 1-2) has now turned into outright failures and near-60s response times. RPS still hasn't moved — confirming the throughput ceiling found in Run 2 is real and hard, not a fluke.

### Next step
Switch to Gunicorn (multi-worker WSGI server) and re-run at 10, 50, and 100 users using the same steps, to see whether RPS increases and the failure rate at 100 users disappears or shrinks.
