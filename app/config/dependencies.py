from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from starlette import status

from app.config.settings import BaseAppSettings, get_settings
from app.database.models.accounts import UserModel
from app.database.session import get_db
from app.exceptions.security import InvalidTokenError, TokenExpiredError
from app.notifications.emails import EmailSender
from app.notifications.interfaces import EmailSenderInterface
from app.security.interfaces import JWTAuthManagerInterface
from app.security.token_manager import JWTAuthManager
from app.storages.interfaces import S3StorageInterface
from app.storages.s3 import S3StorageClient

security = HTTPBearer()


def get_jwt_auth_manager(
    settings: BaseAppSettings = Depends(get_settings),
) -> JWTAuthManagerInterface:
    return JWTAuthManager(
        secret_key_access=settings.SECRET_KEY_ACCESS,
        secret_key_refresh=settings.SECRET_KEY_REFRESH,
        algorithm=settings.JWT_SIGNING_ALGORITHM,
    )


def get_accounts_email_notificator(
    settings: BaseAppSettings = Depends(get_settings),
) -> EmailSenderInterface:
    return EmailSender(
        hostname=settings.EMAIL_HOST,
        port=settings.EMAIL_PORT,
        email=settings.EMAIL_HOST_USER,
        password=settings.EMAIL_HOST_PASSWORD,
        use_tls=settings.EMAIL_USE_TLS,
        template_dir=settings.PATH_TO_EMAIL_TEMPLATES_DIR,
        activation_email_template_name=settings.ACTIVATION_EMAIL_TEMPLATE_NAME,
        activation_complete_email_template_name=(
            settings.ACTIVATION_COMPLETE_EMAIL_TEMPLATE_NAME
        ),
        password_email_template_name=settings.PASSWORD_RESET_TEMPLATE_NAME,
        password_complete_email_template_name=(
            settings.PASSWORD_RESET_COMPLETE_TEMPLATE_NAME
        ),
        payment_success_email_template_name=(
            settings.PAYMENT_SUCCESS_EMAIL_TEMPLATE_NAME
        ),
    )


def get_s3_storage_client(
    settings: BaseAppSettings = Depends(get_settings),
) -> S3StorageInterface:
    return S3StorageClient(
        endpoint_url=settings.S3_STORAGE_ENDPOINT,
        access_key=settings.S3_STORAGE_ACCESS_KEY,
        secret_key=settings.S3_STORAGE_SECRET_KEY,
        bucket_name=settings.S3_BUCKET_NAME,
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
    jwt_manager: JWTAuthManagerInterface = Depends(get_jwt_auth_manager),
) -> UserModel | None:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authentication credentials provided",
        )

    try:
        payload = jwt_manager.decode_access_token(credentials.credentials)
    except TokenExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user = db.get(UserModel, payload["user_id"])
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    return user
