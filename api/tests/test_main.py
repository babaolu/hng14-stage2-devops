"""
Unit tests for the API.
Redis is fully mocked — no live Redis instance required.
"""
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
import main


@pytest.fixture()
def mock_redis():
    """Patch the module-level `r` Redis instance in main.py."""
    mock_instance = MagicMock()
    mock_instance.ping.return_value = True
    with patch.object(main, "r", mock_instance):
        yield mock_instance


@pytest.fixture()
def client(mock_redis):
    return TestClient(main.app)


# ── /health ───────────────────────────────────────────────────────────────────

def test_health_returns_200(client, mock_redis):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_calls_redis_ping(client, mock_redis):
    client.get("/health")
    mock_redis.ping.assert_called_once()


# ── POST /jobs ────────────────────────────────────────────────────────────────

def test_create_job_returns_201(client, mock_redis):
    mock_redis.lpush.return_value = 1
    mock_redis.hset.return_value = 1

    response = client.post("/jobs")

    assert response.status_code == 201
    body = response.json()
    assert "job_id" in body
    assert len(body["job_id"]) == 36  # valid UUID


def test_create_job_pushes_to_queue(client, mock_redis):
    mock_redis.lpush.return_value = 1
    mock_redis.hset.return_value = 1

    response = client.post("/jobs")
    job_id = response.json()["job_id"]

    mock_redis.lpush.assert_called_once()
    queue_name, pushed_id = mock_redis.lpush.call_args[0]
    assert pushed_id == job_id


def test_create_job_sets_queued_status(client, mock_redis):
    mock_redis.lpush.return_value = 1
    mock_redis.hset.return_value = 1

    response = client.post("/jobs")
    job_id = response.json()["job_id"]

    mock_redis.hset.assert_called_once_with(
        f"job:{job_id}", "status", "queued"
    )


# ── GET /jobs/{job_id} ────────────────────────────────────────────────────────

def test_get_job_returns_status(client, mock_redis):
    mock_redis.hget.return_value = "queued"

    response = client.get("/jobs/test-job-id")

    assert response.status_code == 200
    body = response.json()
    assert body["job_id"] == "test-job-id"
    assert body["status"] == "queued"


def test_get_job_completed_status(client, mock_redis):
    mock_redis.hget.return_value = "completed"

    response = client.get("/jobs/some-uuid")

    assert response.status_code == 200
    assert response.json()["status"] == "completed"


def test_get_job_not_found_returns_404(client, mock_redis):
    mock_redis.hget.return_value = None

    response = client.get("/jobs/nonexistent-id")

    assert response.status_code == 404
    assert "detail" in response.json()


def test_get_job_queries_correct_redis_key(client, mock_redis):
    mock_redis.hget.return_value = "queued"

    client.get("/jobs/abc-123")

    mock_redis.hget.assert_called_once_with("job:abc-123", "status")
