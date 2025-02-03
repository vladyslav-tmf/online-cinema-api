from unittest.mock import patch

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
    UserGroupEnum
)
from app.database.models.orders import (
    OrderModel,
    OrderItemModel,
    OrderStatusEnum
)
from app.database.models.movies import MovieModel
from app.config.dependencies import get_current_user


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

client = TestClient(app)


@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def mock_password_validation():
    with patch("app.validators.accounts.validate_password_strength") as mock:
        mock.return_value = True
        yield mock


@pytest.fixture
def user(db):
    existing_group = (db.query(UserGroupModel)
                      .filter_by(name=UserGroupEnum.USER)
                      .first())
    if not existing_group:
        user_group = UserGroupModel(name=UserGroupEnum.USER)
        db.add(user_group)
        db.commit()
    return existing_group or user_group


# @pytest.fixture
# def user(db):
#     user_group = UserGroupModel(name=UserGroupEnum.USER)
#     db.add(user_group)
#     db.commit()
#
#     user = UserModel(
#         email="test@example.com",
#         password="Password123!",
#         group_id=user_group.id
#     )
#     db.add(user)
#     db.commit()
#     return user


@pytest.fixture
def admin(db):
    admin_group = UserGroupModel(name=UserGroupEnum.ADMIN)
    db.add(admin_group)
    db.commit()

    admin = UserModel(
        email="admin@example.com",
        password="Password123!",
        group_id=admin_group.id
    )
    db.add(admin)
    db.commit()
    return admin


@pytest.fixture
def movie(db):
    movie = MovieModel(
        name="Test Movie",
        year=2024,
        time=120,
        imdb=7.5,
        votes=4,
        meta_score=3.5,
        gross=1.2,
        description="Smth new",
        price=9.99,
        certification_id=4
    )
    db.add(movie)
    db.commit()
    return movie


@pytest.fixture
def order(db, user, movie):
    order = OrderModel(user_id=user.id, status=OrderStatusEnum.PENDING)
    db.add(order)
    db.commit()

    order_item = OrderItemModel(
        order_id=order.id,
        movie_id=movie.id,
        price_at_order=movie.price
    )
    db.add(order_item)
    db.commit()

    return order


def test_get_order_list(db, user, order):
    app.dependencies[get_current_user] = lambda: user

    response = client.get("/orders/")
    assert response.status_code == 200
    assert len(response.json()["orders"]) == 1


def test_create_order(db, user, movie):
    app.dependencies[get_current_user] = lambda: user

    response = client.post(
        "/orders/",
        json={"order_items": [{"movie_id": movie.id}]}
    )
    assert response.status_code == 303
    assert response.headers["location"].startswith("/payments/pay?order_id=")


def test_cancel_order(db, user, order):
    app.dependencies[get_current_user] = lambda: user

    response = client.post(f"/order/{order.id}/cancel")
    assert response.status_code == 200

    updated_order = db.query(OrderModel).filter_by(id=order.id).first()
    assert updated_order.status == OrderStatusEnum.CANCELED


def test_delete_order(db, user, order):
    app.dependencies[get_current_user] = lambda: user

    response = client.delete(f"/order/{order.id}")
    assert response.status_code == 204

    deleted_order = db.query(OrderModel).filter_by(id=order.id).first()
    assert deleted_order is None


def test_admin_access(db, admin, order):
    app.dependencies[get_current_user] = lambda: admin

    response = client.get("/orders/")
    assert response.status_code == 200
    assert len(response.json()["orders"]) == 1

    response = client.post(f"/order/{order.id}/cancel")
    assert response.status_code == 200

    response = client.delete(f"/order/{order.id}")
    assert response.status_code == 204
