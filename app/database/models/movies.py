from uuid import uuid4

from sqlalchemy import (
    Integer,
    String,
    Float,
    Text,
    DECIMAL,
    ForeignKey,
    UniqueConstraint
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional

from app.database.models.base import Base


class Base(DeclarativeBase):
    pass


class MoviesGenresModel(Base):
    __tablename__ = "movies_genres"

    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"),
        primary_key=True
    )
    genre_id: Mapped[int] = mapped_column(
        ForeignKey("genres.id", ondelete="CASCADE"),
        primary_key=True
    )


class MovieDirectorsModel(Base):
    __tablename__ = "movies_directors"

    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"),
        primary_key=True
    )
    director_id: Mapped[int] = mapped_column(
        ForeignKey("directors.id", ondelete="CASCADE"),
        primary_key=True
    )


class MoviesStarsModel(Base):
    __tablename__ = "movies_stars"

    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"),
        primary_key=True
    )
    star_id: Mapped[int] = mapped_column(
        ForeignKey("stars.id", ondelete="CASCADE"),
        primary_key=True
    )


class GenreModel(Base):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(Integer, primary_key=True,
                                    autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    movies: Mapped[list["MovieModel"]] = relationship("MovieModel",
                                                      secondary="movie_genres",
                                                      back_populates="genres")


class StarModel(Base):
    __tablename__ = "stars"

    id: Mapped[int] = mapped_column(Integer, primary_key=True,
                                    autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    movies: Mapped[list["MovieModel"]] = relationship("MovieModel",
                                                      secondary="movie_stars",
                                                      back_populates="stars")


class DirectorModel(Base):
    __tablename__ = "directors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True,
                                    autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    movies: Mapped[list["MovieModel"]] = relationship("MovieModel",
                                                      secondary="movie_directors",
                                                      back_populates="directors")


class CertificationModel(Base):
    __tablename__ = "certifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True,
                                    autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    movies: Mapped[list["MovieModel"]] = relationship("MovieModel",
                                                      back_populates="certifications")


class MovieModel(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True,
                                    autoincrement=True)
    uuid: Mapped[str] = mapped_column(String, unique=True,
                                      default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    time: Mapped[int] = mapped_column(Integer, nullable=False)
    imdb: Mapped[float] = mapped_column(Float, nullable=False)
    votes: Mapped[int] = mapped_column(Integer, nullable=False)
    meta_score: Mapped[Optional[float]] = mapped_column(Float)
    gross: Mapped[Optional[float]] = mapped_column(Float)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[float] = mapped_column(DECIMAL(10, 2))
    certification_id: Mapped[int] = mapped_column(Integer, ForeignKey(
        "certifications.id"), nullable=False)

    certification: Mapped[list[CertificationModel]] = relationship(
        "CertificationModel",
        back_populates="movies")
    genres: Mapped[list[GenreModel]] = relationship("GenreModel",
                                                    secondary="movie_genres",
                                                    back_populates="movies")
    directors: Mapped[list[DirectorModel]] = relationship("DirectorModel",
                                                          secondary="movies_directors",
                                                          back_populates="movies")
    stars: Mapped[list[StarModel]] = relationship("StarModel",
                                                  secondary="movies_stars",
                                                  back_populates="movies")

    __table_args__ = (
        UniqueConstraint("name", "year", "time"),
    )
