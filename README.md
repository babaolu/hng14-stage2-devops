# hng14-stage2-devops

# Job Processing System

A containerised multi-service job processing system built with FastAPI, Node.js, and Redis.

## Architecture

```
Browser → Frontend (Node.js :3000)
             └──→ API (FastAPI :8000)
                      └──→ Redis (internal only)
                               ↑
                         Worker (Python)
```

| Service  | Language   | Role                               |
|----------|------------|------------------------------------|
| frontend | Node.js 20 | UI + proxy to API                  |
| api      | Python/FastAPI | Create jobs, serve status      |
| worker   | Python     | Consume queue, process jobs        |
| redis    | Redis 7    | Job queue + status store           |

---

## Prerequisites

| Tool           | Minimum version | Install                         |
|----------------|-----------------|---------------------------------|
| Docker         | 24.x            | https://docs.docker.com/install |
| Docker Compose | 2.20+           | bundled with Docker Desktop     |
| Git            | any             |                                 |

---

## Quick Start (local)

### 1. Clone the repo

```bash
git clone https://github.com/<your-fork>/hng14-stage2-devops.git
cd hng14-stage2-devops
```

### 2. Create your environment file

```bash
cp .env.example .env
```

Edit `.env` and set a strong `REDIS_PASSWORD`. **Never commit `.env`.**

### 3. Build and start the stack

```bash
docker compose up --build -d
```

### 4. Verify all services are healthy

```bash
docker compose ps
```

All four services should show `healthy`:

```
NAME         STATUS          PORTS
redis        Up (healthy)
api          Up (healthy)    0.0.0.0:8000->8000/tcp
worker       Up (healthy)
frontend     Up (healthy)    0.0.0.0:3000->3000/tcp
```

### 5. Open the dashboard

Navigate to **http://localhost:3000** in your browser.

Click **Submit New Job** — the job ID appears and its status updates from `queued` → `completed` within a few seconds.

---

## Environment Variables

All configuration is driven by environment variables. See `.env.example` for the full list.

| Variable         | Service(s)      | Description                              | Default        |
|------------------|-----------------|------------------------------------------|----------------|
| `REDIS_PASSWORD` | api, worker, redis | Redis authentication password         | *(required)*   |
| `QUEUE_NAME`     | api, worker     | Name of the Redis job queue              | `jobs`         |
| `API_URL`        | frontend        | URL the frontend uses to reach the API   | `http://api:8000` |
| `PORT`           | frontend        | Port the frontend listens on             | `3000`         |

---

## API Reference

| Method | Endpoint          | Description              |
|--------|-------------------|--------------------------|
| GET    | `/health`         | Health check             |
| POST   | `/jobs`           | Create a new job         |
| GET    | `/jobs/{job_id}`  | Get status of a job      |

---

## CI/CD Pipeline

The GitHub Actions pipeline runs on every push and has six ordered stages:

```
lint → test → build → security-scan → integration-test → deploy
```

| Stage            | What it does                                                    |
|------------------|-----------------------------------------------------------------|
| lint             | flake8 (Python), eslint (JS), hadolint (Dockerfiles)           |
| test             | pytest + coverage report uploaded as artifact                  |
| build            | Build all 3 images, tag with git SHA + latest, push to local registry |
| security-scan    | Trivy scan — fails pipeline on any CRITICAL CVE                |
| integration-test | Full stack up, submit job, poll to completion, assert status   |
| deploy           | Rolling update on `main` only — new container must pass healthcheck within 60s |

### Required GitHub Secrets (for deploy stage)

| Secret           | Description                                    |
|------------------|------------------------------------------------|
| `DEPLOY_SSH_KEY` | Private SSH key for the production host        |
| `DEPLOY_HOST`    | IP or hostname of the production server        |
| `DEPLOY_USER`    | SSH user on the production server              |
| `REGISTRY_URL`   | URL of your container registry                 |

---

## Stopping the stack

```bash
docker compose down          # stop and remove containers
docker compose down -v       # also remove volumes (wipes Redis data)
```

---

## Bugs fixed from original source

See [FIXES.md](./FIXES.md) for a full list of all 16 bugs found and fixed.
