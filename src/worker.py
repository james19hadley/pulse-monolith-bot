"""
Celery worker entry point for asynchronous background jobs (like Morning Planner).

@Architecture-Map: [APP-CELERY-WORKER]
@Docs: docs/reference/07_ARCHITECTURE_MAP.md
"""
import os
from celery import Celery
from celery.schedules import crontab

# 1. Initialize the Celery application
# We read the REDIS_URL from the environment (defaulting to a local instance if not found)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "pulse_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    # We will auto-discover tasks in the jobs file soon
    include=["src.scheduler.tasks", "src.scheduler.jobs"] 
)

# 2. Celery Configurations
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "catalyst-heartbeat-every-5-minutes": {
            "task": "job_catalyst_heartbeat",
            "schedule": 300.0,
        },
        "stale-session-killer-every-hour": {
            "task": "job_stale_session_killer",
            "schedule": crontab(minute=0),
        },
        "daily-accountability-every-hour": {
            "task": "job_daily_accountability",
            "schedule": crontab(minute=0), # Top of every hour
        },
        "evening-nudge-every-hour": {
            "task": "job_evening_nudge",
            "schedule": crontab(minute=0),
        },
        "morning-planner-every-hour": {
            "task": "job_morning_planner",
            "schedule": crontab(minute=0),
        },
        "midnight-reset-every-hour": {
            "task": "job_midnight_reset",
            "schedule": crontab(minute=0),
        }
    }
)

if __name__ == '__main__':
    celery_app.start()
