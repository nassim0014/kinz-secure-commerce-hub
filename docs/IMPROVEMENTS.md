# Improvements backlog

Real findings from reading the code, tests and CI config directly — not
speculative. Each item says what's wrong, why it matters, and how to verify
a fix.

## Open

1. [x] **`run_etl.py`'s extract/load/run and all of `scheduler.py` had real
   coverage gaps.** `extract_products()`, `extract_sales()`, `load()` and
   `run()` in `src/pipeline/jobs/run_etl.py` were only 57% covered — every
   test exercised `transform_products`/`transform_sales` directly with an
   in-memory DataFrame, so the functions that actually touch the filesystem
   (reading `products.csv`/`sales_2023_2024.csv`, writing
   `products_enriched.csv`/`sales_enriched.csv`, and the `run()` orchestrator)
   were never called by anything in `tests/`. `scheduler.py` was worse: 0%
   coverage, because no test ever imported it at all, so the actual nightly
   cron job wiring (`build_scheduler()`'s `CronTrigger`, `max_instances=1`,
   `coalesce=True`) and the SIGINT/SIGTERM graceful-shutdown handlers in
   `main()` had never run under test. These are exactly the paths most
   likely to break silently in production (a bad raw file, a renamed column,
   a scheduler that doesn't actually shut down gracefully on SIGTERM).
   (done 2026-10-14, PR below) — added `tests/backend/test_etl_pipeline.py`
   (extract success/`FileNotFoundError` paths, the missing-column and
   dropped-rows branches of `transform_*`, `load()`'s stats dict, and a full
   `run()` round-trip against the real seed CSVs) and
   `tests/backend/test_scheduler.py` (`build_scheduler()`'s job config, and
   `main()`'s signal-handler wiring via a fake scheduler so the test never
   calls the real blocking `.start()`). `run_etl.py` 57% → 97% (only the
   `if __name__ == "__main__":` print-and-run line remains uncovered),
   `scheduler.py` 0% → 96% (only its own `__main__` line remains). No bug
   found in the process — both modules behaved correctly; this was a pure
   coverage gap. Verify: `pytest --cov=src/api --cov=src/pipeline
   --cov-report=term-missing` from the repo root.

2. [ ] **`/api/v1/auth/login`'s demo-mode-misconfigured branches are
   untested.** `_get_demo_user()` in `src/api/routes/auth.py` returns `None`
   (and the route answers a generic 401) in two cases: `DEMO_USER_ENABLED=False`
   (line 30) and `DEMO_USER_ENABLED=True` but `DEMO_USER_PASSWORD_HASH` unset
   (line 34, the fail-closed misconfiguration guard). `tests/backend/
   test_security_hardening.py` covers the happy path and wrong-password case
   but neither of these — the exact branch that is supposed to catch "demo
   mode is on but nobody set a password hash" has never actually been
   exercised. Check: monkeypatch `settings.DEMO_USER_ENABLED`/
   `settings.DEMO_USER_PASSWORD_HASH` via `app.dependency_overrides` or a
   fresh `Settings(...)` instance and POST to `/api/v1/auth/login`; assert
   401 with the generic "Invalid email or password" message (never a
   distinguishing error) in both cases.

3. [ ] **`AuditLogger`'s production-vs-dev error handling is unverified.**
   `src/api/security/audit.py` has two safety branches that only matter when
   something is already going wrong: the constructor's non-writable-path
   fallback (lines 49-58, "fall back to /tmp in dev, raise in production")
   and `log()`'s `OSError` handling (lines 78-84, "re-raise in production,
   swallow in dev"). Neither is covered — if the production `raise` ever got
   dropped by mistake, no test would fail. Check: point `AUDIT_LOG_PATH` at
   an unwritable directory (e.g. one with mode `0o000`, or a path under a
   file instead of a directory) with `NODE_ENV=production` vs the default
   dev setting, and assert the production case raises while the dev case
   falls back silently.

4. [ ] **`unhandled_exception_handler` in `main.py` has no test.** The
   handler at `src/api/main.py:143-159` is the last line of defense against
   leaking stack traces to clients ("Never leak stack traces to the
   client"), and it is completely untested — no test ever triggers an
   unhandled exception through the app and checks the response body is the
   generic `{"detail": "Internal server error...", "request_id": ...}`
   shape rather than a traceback. Check: add a throwaway route (or monkeypatch
   an existing one to raise) in a test, hit it through the `TestClient`, and
   assert the 500 response never contains the exception's own message or a
   stack frame.

5. [ ] **`safe_int()` in `src/api/utils/__init__.py` is dead-looking but
   untested.** It's a tolerant int-cast helper documented as "used when
   validating query params," but nothing in `src/api/routes/*.py` currently
   calls it (confirmed via `grep -rn safe_int src/`), and it has no direct
   test either (60% coverage on the file, lines 15-18). Either it's used
   somewhere not yet grepped for and deserves a unit test for its coercion
   behaviour (non-numeric string, `None`, float string, negative), or it's
   unused and should be removed rather than left as an untested, unreferenced
   helper. Check: `grep -rn "safe_int" src/` to confirm current call sites
   before deciding which way to resolve it.
