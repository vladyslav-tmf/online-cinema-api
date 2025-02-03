from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.database.models.movie_interactions import LikeTypeEnum


class BaseLikeSchema(BaseModel):
    like_type: LikeTypeEnum

    model_config = ConfigDict(from_attributes=True)


class MovieLikeCreateSchema(BaseLikeSchema):
    pass


class MovieLikeResponseSchema(BaseLikeSchema):
    id: int
    user_id: int
    movie_id: int
    created_at: datetime


class BaseCommentSchema(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)

    model_config = ConfigDict(from_attributes=True)


class MovieCommentCreateSchema(BaseCommentSchema):
    parent_id: Optional[int] = None


class MovieCommentResponseSchema(BaseCommentSchema):
    id: int
    user_id: int
    movie_id: int
    parent_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    likes_count: int = 0
    is_liked_by_user: bool = False


class CommentLikeResponseSchema(BaseModel):
    id: int
    user_id: int
    comment_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MovieFavoriteResponseSchema(BaseModel):
    id: int
    user_id: int
    movie_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MovieRatingCreateSchema(BaseModel):
    rating: int = Field(..., ge=1, le=10)

    model_config = ConfigDict(from_attributes=True)

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, value):
        if not 1 <= value <= 10:
            raise ValueError("Rating must be an integer between 1 and 10")
        return value


class MovieRatingResponseSchema(MovieRatingCreateSchema):
    id: int
    user_id: int
    movie_id: int
    created_at: datetime
    updated_at: datetime
