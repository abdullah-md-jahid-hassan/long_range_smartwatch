from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "beat-heartbeat": {
        "task": "core.tasks.beat_heartbeat",
        "schedule": crontab(minute="*/1"),
    },
}
