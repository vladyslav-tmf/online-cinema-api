from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "delete_expired_activation_tokens_every_hour": {
        "task": "tasks.delete_expired_activation_tokens",
        "schedule": crontab(minute=0, hour="*/1"),
    },
}
