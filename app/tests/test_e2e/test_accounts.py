import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.session import get_db
from app.database.models.base import Base
from app.database.models.accounts import (
    UserModel,
    UserGroupModel,
    UserGroupEnum,
    ActivationTokenModel
)
from app.config.dependencies import (
    get_accounts_email_notificator,
    get_jwt_auth_manager
)
from app.notifications.interfaces import EmailSenderInterface
from app.security.interfaces import JWTAuthManagerInterface


SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = get_db


class MockEmailSender(EmailSenderInterface):
    def send_activation_email(self, email: str, activation_link: str) -> None:
        pass

    def send_activation_complete_email(self, email: str, login_link: str) -> None:
        pass

    def send_password_reset_email(self, email: str, reset_link: str) -> None:
        pass

    def send_password_reset_complete_email(self, email: str, login_link: str) -> None:
        pass


app.dependency_overrides[get_accounts_email_notificator] = lambda: MockEmailSender()


class MockJWTManager(JWTAuthManagerInterface):
    def create_access_token(self, data: dict) -> str:
        return "mock_access_token"

    def create_refresh_token(self, data: dict) -> str:
        return "mock_refresh_token"

    def decode_access_token(self, token: str) -> dict:
        return {"user_id": 1}

    def decode_refresh_token(self, token: str) -> dict:
        return {"user_id": 1}


app.dependency_overrides[get_jwt_auth_manager] = lambda: MockJWTManager()

client = TestClient(app)


@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def user_group(db):
    group = UserGroupModel(name=UserGroupEnum.USER)
    db.add(group)
    db.commit()
    return group


@pytest.fixture
def admin_group(db):
    group = UserGroupModel(name=UserGroupEnum.ADMIN)
    db.add(group)
    db.commit()
    return group


def test_register_user(db, user_group):
    response = client.post(
        "/accounts/register/",
        json={"email": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["email"] == "test@example.com"


def test_activate_account(db, user_group):
    user = UserModel(
        email="test@example.com",
        password="testpassword",
        group_id=user_group.id
    )
    db.add(user)
    db.commit()

    activation_token = ActivationTokenModel(user_id=user.id)
    db.add(activation_token)
    db.commit()

    response = client.post(
        "/accounts/activate/",
        json={"email": "test@example.com", "token": activation_token.token}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "User account activated successfully."


def test_login_user(db, user_group):
    user = UserModel(
        email="test@example.com",
        password="testpassword",
        group_id=user_group.id,
        is_active=True
    )
    db.add(user)
    db.commit()

    response = client.post(
        "/accounts/login/",
        json={"email": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 201
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()


def test_refresh_token(db, user_group):
    user = UserModel(
        email="test@example.com",
        password="testpassword",
        group_id=user_group.id,
        is_active=True
    )
    db.add(user)
    db.commit()

    response = client.post(
        "/accounts/refresh/",
        json={"refresh_token": "mock_refresh_token"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
