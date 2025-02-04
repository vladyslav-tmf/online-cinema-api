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
from app.database.models.movies import (
    MovieModel,
    GenreModel,
    DirectorModel,
    StarModel,
    CertificationModel
)


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


@pytest.fixture
def user(db):
    user_group = UserGroupModel(name=UserGroupEnum.USER)
    db.add(user_group)
    db.commit()

    user = UserModel(
        email="test@example.com",
        password="password",
        group_id=user_group.id
    )
    db.add(user)
    db.commit()
    return user


@pytest.fixture
def admin(db):
    admin_group = UserGroupModel(name=UserGroupEnum.ADMIN)
    db.add(admin_group)
    db.commit()

    admin = UserModel(
        email="admin@example.com",
        password="password",
        group_id=admin_group.id
    )
    db.add(admin)
    db.commit()
    return admin


@pytest.fixture
def movie(db):
    certification = CertificationModel(name="PG")
    genre = GenreModel(name="Action")
    director = DirectorModel(name="John Doe")
    star = StarModel(name="Jane Doe")

    db.add_all([certification, genre, director, star])
    db.commit()

    movie = MovieModel(
        name="Test Movie",
        year=2023,
        time=120,
        imdb=8.5,
        votes=1000,
        meta_score=85,
        gross=1000000,
        description="Test movie description",
        price=9.99,
        certification_id=certification.id
    )
    movie.genres.append(genre)
    movie.directors.append(director)
    movie.stars.append(star)

    db.add(movie)
    db.commit()
    return movie


def test_get_movies(db, movie):
    response = client.get("/movies/")
    assert response.status_code == 200
    assert len(response.json()["movies"]) == 1
    assert response.json()["movies"][0]["name"] == "Test Movie"


def test_get_movie(db, movie):
    response = client.get(f"/movies/{movie.id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Movie"


def test_create_movie(db, admin):
    login_response = client.post(
        "/accounts/login/",
        json={"email": "admin@example.com", "password": "password"}
    )
    assert login_response.status_code == 201
    access_token = login_response.json()["access_token"]

    movie_data = {
        "name": "New Movie",
        "year": 2023,
        "time": 130,
        "imdb": 7.5,
        "votes": 500,
        "meta_score": 75,
        "gross": 500000,
        "description": "New movie description",
        "price": 12.99,
        "certification_id": 1,
        "genre_ids": [1],
        "director_ids": [1],
        "star_ids": [1]
    }

    response = client.post(
        "/movies/",
        json=movie_data,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "New Movie"


def test_update_movie(db, admin, movie):
    login_response = client.post(
        "/accounts/login/",
        json={"email": "admin@example.com", "password": "password"}
    )
    assert login_response.status_code == 201
    access_token = login_response.json()["access_token"]

    update_data = {
        "name": "Updated Movie",
        "year": 2024
    }

    response = client.put(
        f"/movies/{movie.id}",
        json=update_data, headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Movie"
    assert response.json()["year"] == 2024


def test_delete_movie(db, admin, movie):
    login_response = client.post(
        "/accounts/login/",
        json={"email": "admin@example.com", "password": "password"}
    )
    assert login_response.status_code == 201
    access_token = login_response.json()["access_token"]

    response = client.delete(
        f"/movies/{movie.id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 204

    get_response = client.get(f"/movies/{movie.id}")
    assert get_response.status_code == 404
