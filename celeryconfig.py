from celery.schedules import timedelta

broker_url = "redis://localhost:6379/0"
result_backend = "redis://localhost:6379/0"

CELERY_BEAT_SCHEDULE = {
    "delete_expired_activation_tokens_every_hour": {
        "task": "tasks.delete_expired_activation_tokens",
        "schedule": timedelta(hours=26),
    },
}

timezone = "UTC"
