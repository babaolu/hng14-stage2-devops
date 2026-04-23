# FIXES.md

Every bug found in the original source, with file, line, description, and fix.

---

## BUG-01 — `api/.env` committed to git with real credentials
**File:** `api/.env` (entire file)  
**Problem:** A real `.env` file containing `REDIS_PASSWORD=supersecretpassword123` was committed directly into the repository and is present in git history. This violates the task rules and is a production security incident.  
**Fix:** Added `api/.env` and `.env` to `.gitignore`. Created `.env.example` with placeholder values. The actual secret must be scrubbed from git history using `git filter-branch` or BFG Repo Cleaner before the repository is made public.

---

## BUG-02 — `api/main.py` Redis host hardcoded to `localhost`
**File:** `api/main.py`, line 8  
**Problem:** `redis.Redis(host="localhost", port=6379)` — inside Docker, containers communicate via service names, not `localhost`. The API would fail to connect to Redis in any containerised environment.  
**Fix:** Changed to `redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=int(os.getenv("REDIS_PORT", 6379)), ...)` — host is read from the `REDIS_HOST` environment variable, defaulting to `"redis"` (the Compose service name).

---

## BUG-03 — `worker/worker.py` Redis host hardcoded to `localhost`
**File:** `worker/worker.py`, line 5  
**Problem:** Same as BUG-02. `redis.Redis(host="localhost", port=6379)` would always fail inside Docker.  
**Fix:** Same pattern — reads `REDIS_HOST` and `REDIS_PORT` from environment variables.

---

## BUG-04 — `frontend/app.js` API URL hardcoded to `localhost`
**File:** `frontend/app.js`, line 6  
**Problem:** `const API_URL = "http://localhost:8000"` — the frontend container cannot reach the API container via `localhost`. In Docker, `localhost` refers to the frontend container itself.  
**Fix:** Changed to `const API_URL = process.env.API_URL || "http://api:8000"` — reads from the `API_URL` environment variable.

---

## BUG-05 — `api/main.py` Redis password not passed to client
**File:** `api/main.py`, line 8  
**Problem:** `REDIS_PASSWORD` was defined in `.env` but never passed to the Redis client. If Redis requires authentication (which it should in production), every command would return `NOAUTH Authentication required`.  
**Fix:** Added `password=os.getenv("REDIS_PASSWORD")` to the Redis constructor.

---

## BUG-06 — `worker/worker.py` Redis password not passed to client
**File:** `worker/worker.py`, line 5  
**Problem:** Same as BUG-05 — password not passed, so the worker would be rejected by an auth-enabled Redis.  
**Fix:** Added `password=os.getenv("REDIS_PASSWORD")` to the Redis constructor.

---

## BUG-07 — `worker/worker.py` `signal` imported but never used
**File:** `worker/worker.py`, line 4  
**Problem:** `import signal` was present but no signal handlers were registered. On `docker stop`, the container would receive SIGTERM, wait the stop timeout (default 10s), then be hard-killed (SIGKILL) mid-job — silently corrupting any in-flight job.  
**Fix:** Registered `SIGTERM` and `SIGINT` handlers that set a `shutdown_requested` flag so the worker finishes the current job before exiting cleanly.

---

## BUG-08 — `worker/worker.py` no error handling — one Redis error kills the worker permanently
**File:** `worker/worker.py`, lines 14–18  
**Problem:** The bare `while True` loop had no try/except. A transient Redis connection error (network blip, Redis restart) would raise an unhandled exception and kill the worker process entirely. It would not recover without a manual container restart.  
**Fix:** Wrapped the loop body in try/except with logging and a 5-second backoff before reconnecting.

---

## BUG-09 — `api/main.py` returns HTTP 200 for "not found" jobs
**File:** `api/main.py`, lines 18–20  
**Problem:** `return {"error": "not found"}` returned a 200 OK response for missing jobs. This breaks any consumer that checks HTTP status codes (the frontend, health checks, the integration test).  
**Fix:** Replaced with `raise HTTPException(status_code=404, detail="Job not found")`.

---

## BUG-10 — `api/main.py` no `/health` endpoint
**File:** `api/main.py`  
**Problem:** No health endpoint existed. Docker's `HEALTHCHECK`, Compose `depends_on: condition: service_healthy`, and the CI integration test all require a `/health` route to verify the service is live.  
**Fix:** Added `GET /health` that calls `r.ping()` and returns `{"status": "ok"}`.

---

## BUG-11 — `frontend/app.js` no `/health` endpoint
**File:** `frontend/app.js`  
**Problem:** Same as BUG-10 — no health endpoint for Docker healthchecks.  
**Fix:** Added `GET /health` returning `{"status": "ok"}`.

---

## BUG-12 — `api/requirements.txt` no pinned versions
**File:** `api/requirements.txt`  
**Problem:** `fastapi`, `uvicorn`, `redis` with no version pins. Each build could pull a different version, making builds non-reproducible and liable to silent breakage.  
**Fix:** Pinned to `fastapi==0.115.0`, `uvicorn[standard]==0.30.6`, `redis==5.0.8`.

---

## BUG-13 — `worker/requirements.txt` no pinned version
**File:** `worker/requirements.txt`  
**Problem:** `redis` with no version pin — same reproducibility issue as BUG-12.  
**Fix:** Pinned to `redis==5.0.8`.

---

## BUG-14 — No `package-lock.json` in frontend
**File:** `frontend/` (missing file)  
**Problem:** Without a lockfile, `npm install` resolves the dependency graph fresh each build — different machines or build times can get different versions. The Dockerfile should use `npm ci` (requires a lockfile) for reproducible installs.  
**Fix:** Run `npm install` locally to generate `package-lock.json`, commit it, and use `npm ci --only=production` in the Dockerfile.

---

## BUG-15 — API container would bind to `127.0.0.1` by default
**File:** `api/main.py` (no uvicorn entrypoint defined)  
**Problem:** Without an explicit `--host 0.0.0.0`, uvicorn defaults to `127.0.0.1`, which is unreachable from other containers or the host. No other container could call the API.  
**Fix:** The Dockerfile CMD explicitly passes `--host 0.0.0.0 --port 8000`.

---

## BUG-16 — `api/.env` missing trailing newline
**File:** `api/.env`, line 2  
**Problem:** `APP_ENV=production` has no trailing newline. Some env-file parsers silently drop the last variable if the file doesn't end with a newline.  
**Fix:** Moot — the file is removed entirely (see BUG-01). Documented for completeness.
