from sqlalchemy.orm import Session

from app.database.models.accounts import UserGroupEnum, UserGroupModel


def init_user_groups(db: Session) -> None:
    for group_name in UserGroupEnum:
        existing_group = db.query(UserGroupModel).filter_by(name=group_name).first()
        if not existing_group:
            group = UserGroupModel(name=group_name)
            db.add(group)

    db.commit()
