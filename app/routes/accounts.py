from datetime import datetime, timezone
from typing import cast

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from config.dependencies import get_accounts_email_notificator
from database.models.accounts import (
    ActivationTokenModel,
    PasswordResetTokenModel,
    UserGroupEnum,
    UserGroupModel,
    UserModel,
)
from database.session import get_db
from notifications.interfaces import EmailSenderInterface
from schemas.accounts import (
    MessageResponseSchema,
    PasswordResetCompleteRequestSchema,
    PasswordResetRequestSchema,
    UserActivationRequestSchema,
    UserRegistrationRequestSchema,
    UserRegistrationResponseSchema,
)

router = APIRouter()


@router.post("/register/", response_model=UserRegistrationResponseSchema)
def register_user(
    user_data: UserRegistrationRequestSchema,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    email_sender: EmailSenderInterface = Depends(get_accounts_email_notificator),
) -> UserRegistrationResponseSchema:
    existing_user = db.query(UserModel).filter_by(email=user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A user with this email {user_data.email} already exists.",
        )

    user_group = db.query(UserGroupModel).filter_by(name=UserGroupEnum.USER).first()

    try:
        new_user = UserModel.create(
            email=str(user_data.email),
            raw_password=user_data.password,
            group_id=user_group.id,
        )
        db.add(new_user)
        db.flush()

        activation_token = ActivationTokenModel(user_id=new_user.id)
        db.add(activation_token)

        db.commit()
        db.refresh(new_user)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during user creation.",
        )
    else:
        activation_link = "http://127.0.0.1/accounts/activate/"

        background_tasks.add_task(
            email_sender.send_activation_email, new_user.email, activation_link
        )

        return UserRegistrationResponseSchema.model_validate(new_user)


@router.post("/activate/", response_model=MessageResponseSchema)
def activate_account(
    activation_data: UserActivationRequestSchema,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    email_sender: EmailSenderInterface = Depends(get_accounts_email_notificator),
) -> MessageResponseSchema:
    token_record = (
        db.query(ActivationTokenModel)
        .join(UserModel)
        .filter(
            UserModel.email == activation_data.email,
            ActivationTokenModel.token == activation_data.token,
        )
        .first()
    )

    if not token_record or cast(datetime, token_record.expires_at).replace(
        tzinfo=timezone.utc
    ) < datetime.now(timezone.utc):
        if token_record:
            db.delete(token_record)
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired activation token.",
        )

    user = token_record.user
    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is already active.",
        )

    user.is_active = True
    db.delete(token_record)
    db.commit()

    login_link = "http://127.0.0.1/accounts/login/"

    background_tasks.add_task(
        email_sender.send_activation_complete_email,
        str(activation_data.email),
        login_link,
    )

    return MessageResponseSchema(message="User account activated successfully.")


@router.post("/password-reset/request/", response_model=MessageResponseSchema)
def request_password_reset_token(
    data: PasswordResetRequestSchema,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    email_sender: EmailSenderInterface = Depends(get_accounts_email_notificator),
) -> MessageResponseSchema:
    user = db.query(UserModel).filter_by(email=data.email).first()

    if not user or not user.is_active:
        return MessageResponseSchema(
            message=(
                "If you are registered, you will receive an email with instructions."
            )
        )

    db.query(PasswordResetTokenModel).filter_by(user_id=user.id).delete()

    reset_token = PasswordResetTokenModel(user_id=cast(int, user.id))
    db.add(reset_token)
    db.commit()

    password_reset_complete_link = "http://127.0.0.1/accounts/password-reset-complete/"

    background_tasks.add_task(
        email_sender.send_password_reset_email,
        str(data.email),
        password_reset_complete_link,
    )

    return MessageResponseSchema(
        message="If you are registered, you will receive an email with instructions."
    )


@router.post("/reset-password/complete/", response_model=MessageResponseSchema)
def reset_password(
    data: PasswordResetCompleteRequestSchema,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    email_sender: EmailSenderInterface = Depends(get_accounts_email_notificator),
) -> MessageResponseSchema:
    user = db.query(UserModel).filter_by(email=data.email).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email or token."
        )

    token_record = db.query(PasswordResetTokenModel).filter_by(user_id=user.id).first()

    expires_at = cast(datetime, token_record.expires_at).replace(tzinfo=timezone.utc)

    if (
        not token_record
        or token_record.token != data.token
        or expires_at < datetime.now(timezone.utc)
    ):
        if token_record:
            db.delete(token_record)
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email or token."
        )

    try:
        user.password = data.password
        db.delete(token_record)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while resetting the password.",
        )

    login_link = "http://127.0.0.1/accounts/login/"

    background_tasks.add_task(
        email_sender.send_password_reset_complete_email, str(data.email), login_link
    )

    return MessageResponseSchema(message="Password reset successfully.")
