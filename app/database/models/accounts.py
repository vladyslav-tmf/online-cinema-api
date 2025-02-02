import enum
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from database.models.base import Base
from security.passwords import hash_password, verify_password
from security.utils import generate_secure_token
from validators.accounts import validate_email, validate_password_strength


class UserGroupEnum(str, enum.Enum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


class GenderEnum(str, enum.Enum):
    MAN = "man"
    WOMAN = "woman"


class UserGroupModel(Base):
    __tablename__ = "user_groups"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[UserGroupEnum] = mapped_column(
        Enum(UserGroupEnum), nullable=False, unique=True
    )

    users: Mapped[list["UserModel"]] = relationship("UserModel", back_populates="group")

    def __repr__(self):
        return f"<UserGroupModel(id={self.id}, name={self.name})>"


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    _hashed_password: Mapped[str] = mapped_column(
        "hashed_password", String(255), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    group_id: Mapped[int] = mapped_column(
        ForeignKey("user_groups.id", ondelete="CASCADE"), nullable=False
    )
    group: Mapped["UserGroupModel"] = relationship(
        "UserGroupModel", back_populates="users"
    )

    activation_token: Mapped[Optional["ActivationTokenModel"]] = relationship(
        "ActivationTokenModel", back_populates="user", cascade="all, delete-orphan"
    )

    password_reset_token: Mapped[Optional["PasswordResetTokenModel"]] = relationship(
        "PasswordResetTokenModel", back_populates="user", cascade="all, delete-orphan"
    )

    refresh_tokens: Mapped[list["RefreshTokenModel"]] = relationship(
        "RefreshTokenModel", back_populates="user", cascade="all, delete-orphan"
    )

    profile: Mapped[Optional["UserProfileModel"]] = relationship(
        "UserProfileModel", back_populates="user", cascade="all, delete-orphan"
    )

    payments: Mapped[list["PaymentModel"]] = relationship(
        "PaymentModel", back_populates="user", cascade="all, delete-orphan"
    )

    movie_likes: Mapped[list["MovieLikeModel"]] = relationship(
        "MovieLikeModel", back_populates="user", cascade="all, delete-orphan"
    )

    movie_comments: Mapped[list["MovieCommentModel"]] = relationship(
        "MovieCommentModel", back_populates="user", cascade="all, delete-orphan"
    )

    comment_likes: Mapped[list["CommentLikeModel"]] = relationship(
        "CommentLikeModel", back_populates="user", cascade="all, delete-orphan"
    )

    favorite_movies: Mapped[list["MovieFavoriteModel"]] = relationship(
        "MovieFavoriteModel", back_populates="user", cascade="all, delete-orphan"
    )

    movie_ratings: Mapped[list["MovieRatingModel"]] = relationship(
        "MovieRatingModel", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<UserModel(id={self.id}, email={self.email}, is_active={self.is_active})>"
        )

    def has_group(self, group_name: UserGroupEnum) -> bool:
        return self.group.name == group_name

    @classmethod
    def create(
        cls, email: str, raw_password: str, group_id: int | Mapped[int]
    ) -> "UserModel":
        user = cls(email=email, group_id=group_id)
        user.password = raw_password
        return user

    @property
    def password(self) -> None:
        raise AttributeError(
            "Password is write-only. Use the setter to set the password."
        )

    @password.setter
    def password(self, raw_password: str) -> None:
        validate_password_strength(raw_password)
        self._hashed_password = hash_password(raw_password)

    def verify_password(self, raw_password: str) -> bool:
        return verify_password(raw_password, self._hashed_password)

    @validates("email")
    def validate_email(self, key, value):
        return validate_email(value.lower())


class UserProfileModel(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    avatar: Mapped[Optional[str]] = mapped_column(String(255))
    gender: Mapped[Optional[GenderEnum]] = mapped_column(Enum(GenderEnum))
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date)
    info: Mapped[Optional[str]] = mapped_column(Text)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    user: Mapped[UserModel] = relationship("UserModel", back_populates="profile")

    __table_args__ = (UniqueConstraint("user_id"),)

    def __repr__(self):
        return (
            f"<UserProfileModel(id={self.id}, first_name={self.first_name}, "
            f"last_name={self.last_name}, gender={self.gender}, "
            f"date_of_birth={self.date_of_birth})>"
        )


class TokenBaseModel(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    token: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, default=generate_secure_token
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc) + timedelta(days=1),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )


class ActivationTokenModel(TokenBaseModel):
    __tablename__ = "activation_tokens"

    user: Mapped[UserModel] = relationship(
        "UserModel", back_populates="activation_token"
    )

    __table_args__ = (UniqueConstraint("user_id"),)

    def __repr__(self):
        return (
            f"<ActivationTokenModel(id={self.id}, token={self.token}, "
            f"expires_at={self.expires_at})>"
        )


class PasswordResetTokenModel(TokenBaseModel):
    __tablename__ = "password_reset_tokens"

    user: Mapped[UserModel] = relationship(
        "UserModel", back_populates="password_reset_token"
    )

    __table_args__ = (UniqueConstraint("user_id"),)

    def __repr__(self):
        return (
            f"<PasswordResetTokenModel(id={self.id}, token={self.token}, "
            f"expires_at={self.expires_at})>"
        )


class RefreshTokenModel(TokenBaseModel):
    __tablename__ = "refresh_tokens"

    user: Mapped[UserModel] = relationship("UserModel", back_populates="refresh_tokens")
    token: Mapped[str] = mapped_column(
        String(512), unique=True, nullable=False, default=generate_secure_token
    )

    @classmethod
    def create(cls, user_id: int, days_valid: int, token: str) -> "RefreshTokenModel":
        expires_at = datetime.now(timezone.utc) + timedelta(days=days_valid)
        return cls(user_id=user_id, expires_at=expires_at, token=token)

    def __repr__(self):
        return (
            f"<RefreshTokenModel(id={self.id}, token={self.token}, "
            f"expires_at={self.expires_at})>"
        )
