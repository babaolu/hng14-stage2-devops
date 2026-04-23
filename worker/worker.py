import redis
import time
import os
import signal
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

shutdown_requested = False


def handle_sigterm(signum, frame):
    global shutdown_requested
    logger.info("SIGTERM received — finishing current job then exiting")
    shutdown_requested = True


signal.signal(signal.SIGTERM, handle_sigterm)
signal.signal(signal.SIGINT, handle_sigterm)


def get_redis_client():
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=True,
    )


def process_job(r, job_id):
    logger.info(f"Processing job {job_id}")
    time.sleep(2)  # simulate work
    r.hset(f"job:{job_id}", "status", "completed")
    logger.info(f"Done: {job_id}")


def main():
    r = None
    while not shutdown_requested:
        try:
            if r is None:
                r = get_redis_client()
                r.ping()
                logger.info("Connected to Redis")

            job = r.brpop("job", timeout=5)
            if job:
                _, job_id = job
                process_job(r, job_id)

        except redis.exceptions.ConnectionError as e:
            logger.error(f"Redis connection error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

    logger.info("Worker shut down cleanly")
    sys.exit(0)


if __name__ == "__main__":
    main()
