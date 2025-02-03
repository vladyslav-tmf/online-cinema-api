from celery.schedules import crontab

broker_url = "redis://localhost:6379/0"
result_backend = "redis://localhost:6379/0"

CELERY_BEAT_SCHEDULE = {
    "delete_expired_activation_tokens_every_hour": {
        "task": "tasks.delete_expired_activation_tokens",
        "schedule": crontab(minute=0, hour="*/1"),
    },
}

timezone = "UTC"
