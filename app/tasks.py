from celery import Celery
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models.accounts import ActivationTokenModel

celery = Celery("tasks", broker="redis://localhost:6379/0")


@celery.task
def delete_expired_activation_tokens():
    db: Session = next(get_db())
    current_time = datetime.now(timezone.utc)

    expired_tokens = (
        db.query(ActivationTokenModel)
        .filter(ActivationTokenModel.expires_at < current_time)
        .all()
    )

    for token in expired_tokens:
        db.delete(token)

    db.commit()
    db.close()
