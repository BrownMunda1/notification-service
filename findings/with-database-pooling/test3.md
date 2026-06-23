## Run 5 — 100 users, with Django native connection pooling (psycopg3 pool, min_size=2, max_size=20)

**Date:** 2026-06-23
**Config:** 100 users, spawn rate 2/s. Same as Run 3, but with connection pooling now enabled.
**Endpoint under test:** `POST /api/v1/notifications/send/`
**Server:** `manage.py runserver` (still the dev server)

| Type | Name | # Requests | # Fails | Median (ms) | 95%ile (ms) | 99%ile (ms) | Average (ms) | Min (ms) | Max (ms) | Avg size (bytes) | Current RPS | Current Failures/s |
|------|------|-----------:|--------:|------------:|------------:|------------:|-------------:|---------:|---------:|------------------:|------------:|--------------------:|
| POST | /api/v1/notifications/send/ | 247 | 15 | 26000 | 58000 | 61000 | 25837.82 | 2019 | 61409 | 15391.08 | 3.2 | 0.9 |
| **Aggregated** | | 247 | 15 | 26000 | 58000 | 61000 | 25837.82 | 2019 | 61409 | 15391.08 | 3.2 | 0.9 |

### Error captured (from Django logs, on a failed request)

```
django.db.utils.OperationalError: couldn't get a connection after 30.00 sec
psycopg_pool.PoolTimeout: couldn't get a connection after 30.00 sec
```

### Comparison vs. Run 3 (100 users, no pooling)

| Metric | Run 3 (no pooling) | Run 5 (with pooling) |
|---|---:|---:|
| Failure rate | 13% | 6% |
| Failure type | Postgres hard rejection (`remaining connection slots are reserved for roles with the SUPERUSER attribute`) | Django pool timeout (`couldn't get a connection after 30.00 sec`) |
| Median latency | 47000 ms | 26000 ms |

### Observations
- **Failure rate roughly halved** (13% → 6%) and the **failure mode changed entirely** — Postgres itself is no longer being directly overwhelmed. The pool is correctly absorbing and queueing connection requests instead of flooding the database.
- **Failures only started appearing after ~210 successful requests**, not from the start. This is the key insight: the pool didn't fail because too many users connected at once — it failed because individual connections were held too long (since each request itself takes 17-26s+ due to the dev server bottleneck). Over time, all 20 pooled connections became simultaneously occupied by slow, long-running requests, and new requests queuing behind them eventually hit the 30-second pool timeout.
- This confirms pooling fixed the *symptom* at the DB level, but the *root cause* — slow per-request processing under concurrency — is unchanged. The two bottlenecks are stacked: a small/slow server holds connections too long → pool eventually saturates anyway under sustained load, just later and with a softer failure mode than a raw DB rejection.

### Conclusion
Connection pooling is working as intended — it's a real, measurable improvement (lower failure rate, more graceful failure mode, lower latency). But it cannot fully solve the underlying problem alone, because the pool's connections stay tied up for as long as the slow dev server takes to process each request. The fundamental fix is still the same one identified back in Run 2: move off `manage.py runserver` to a server that can actually process requests concurrently (e.g. Gunicorn with multiple workers), which should free up pooled connections much faster and reduce both latency and pool-timeout failures.

### Next step
Set up Gunicorn and re-run the same staged tests (10 / 50 / 100 users) with pooling still enabled, to see the combined effect of both fixes together.
