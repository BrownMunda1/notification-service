# Load Test Results

This file logs load test runs against the notifications endpoint, with config, raw metrics, observations, and hypotheses for each run.

---

## Run 1 — Gunicorn, sync workers, 4 workers, 50 users

**Date:** 2026-06-25

**Config:**
- Server: Gunicorn
- Worker class: `sync`
- Workers: 4 (machine has 8 cores via `nproc`)
- Bind: `0.0.0.0:8000`
- DB: PostgreSQL (WSL2), psycopg3 native connection pooling enabled
- Locust users: 50
- Endpoint: `POST /api/v1/notifications/send/`

**Results:**

| Metric | Value |
|---|---|
| Total Requests | 181 |
| Failures | 0 (0%) |
| RPS | 2.13 |
| Median (ms) | 20000 |
| 95%ile (ms) | 21000 |
| 99%ile (ms) | 21000 |
| Average (ms) | 15455.23 |
| Min (ms) | 1772 |
| Max (ms) | 21693 |
| Avg response size (bytes) | 142.78 |

**Observations:**
- 0% failure rate — unlike earlier `runserver` tests, requests aren't being rejected (e.g. no connection pool exhaustion errors surfacing as failures).
- Median latency started lower (~2000ms) early in the run and grew as the test progressed, eventually settling around 20000ms.
- Even the **minimum** latency recorded was 1772ms — no request completed fast, not even the first ones.
- RPS is very low (2.13) relative to 4 workers and 50 concurrent users.

**Hypothesis:**
- This doesn't look like a rejection/exhaustion failure mode anymore (0% failures) — it looks like a **queueing** problem. With only 4 sync workers, each handling one request at a time, 50 concurrent users' worth of requests are queueing up behind the 4 that are actively being processed. As more requests pile into the queue over the test duration, wait time before a worker even picks them up grows — which would explain why median latency climbed over time rather than staying flat.
- Need to check: is the per-request *processing* time itself slow (e.g. a slow DB query, view logic, serializer), or is nearly all of the latency just queue wait time? Worth isolating by hitting the endpoint with a single user and checking its raw response time in isolation.

---
