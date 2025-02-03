from datetime import datetime
from enum import Enum

from sqlalchemy import (
    DateTime,
    Enum as SQLAlchemyEnum,
    Float,
    ForeignKey,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import Base


class LikeTypeEnum(str, Enum):
    LIKE = "like"
    DISLIKE = "dislike"


class MovieLikeModel(Base):
    __tablename__ = "movie_likes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"), nullable=False
    )
    like_type: Mapped[LikeTypeEnum] = mapped_column(
        SQLAlchemyEnum(LikeTypeEnum), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["UserModel"] = relationship(back_populates="movie_likes")
    movie: Mapped["MovieModel"] = relationship(back_populates="likes")

    __table_args__ = (
        UniqueConstraint("user_id", "movie_id", name="unique_movie_like"),
    )


class MovieCommentModel(Base):
    __tablename__ = "movie_comments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"), nullable=False
    )
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("movie_comments.id", ondelete="CASCADE"), nullable=True
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped["UserModel"] = relationship(back_populates="movie_comments")
    movie: Mapped["MovieModel"] = relationship(back_populates="comments")
    parent: Mapped["MovieCommentModel"] = relationship(
        "MovieCommentModel", remote_side=[id], back_populates="replies"
    )
    replies: Mapped[list["MovieCommentModel"]] = relationship(
        "MovieCommentModel", back_populates="parent", cascade="all, delete-orphan"
    )
    likes: Mapped[list["CommentLikeModel"]] = relationship(
        back_populates="comment", cascade="all, delete-orphan"
    )


class CommentLikeModel(Base):
    __tablename__ = "comment_likes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    comment_id: Mapped[int] = mapped_column(
        ForeignKey("movie_comments.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["UserModel"] = relationship(back_populates="comment_likes")
    comment: Mapped["MovieCommentModel"] = relationship(back_populates="likes")

    __table_args__ = (
        UniqueConstraint("user_id", "comment_id", name="unique_comment_like"),
    )


class MovieFavoriteModel(Base):
    __tablename__ = "movie_favorites"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["UserModel"] = relationship(back_populates="favorite_movies")
    movie: Mapped["MovieModel"] = relationship(back_populates="favorited_by")

    __table_args__ = (
        UniqueConstraint("user_id", "movie_id", name="unique_movie_favorite"),
    )


class MovieRatingModel(Base):
    __tablename__ = "movie_ratings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"), nullable=False
    )
    rating: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped["UserModel"] = relationship(back_populates="movie_ratings")
    movie: Mapped["MovieModel"] = relationship(back_populates="ratings")

    __table_args__ = (
        UniqueConstraint("user_id", "movie_id", name="unique_movie_rating"),
    )
