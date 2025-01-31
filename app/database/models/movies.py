from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database.models.base import Base


class GenreModel(Base):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    movies = relationship("MovieModel", secondary="movie_genres", back_populates="genres")

