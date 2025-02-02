from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from uuid import UUID


class GenreSchema(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class StarSchema(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class DirectorSchema(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class CertificationSchema(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class MovieSchema(BaseModel):
    id: int
    uuid: UUID
    name: str
    year: int
    time: int
    imdb: float
    votes: int
    meta_score: float | None = None
    gross: float | None = None
    description: str
    price: float
    certification: CertificationSchema
    genres: list[GenreSchema]
    directors: list[DirectorSchema]
    stars: list[StarSchema]
    likes_count: int = 0
    dislikes_count: int = 0
    comments_count: int = 0
    favorites_count: int = 0
    average_rating: float | None = None
    is_liked_by_user: bool = False
    is_disliked_by_user: bool = False
    is_favorited_by_user: bool = False
    user_rating: float | None = None

    model_config = ConfigDict(from_attributes=True)


class PaginationSchema(BaseModel):
    movies: list[MovieSchema]
    prev_page: str | None = None
    next_page: str | None = None
    total_items: int
    total_pages: int

    model_config = ConfigDict(from_attributes=True)


class MovieListItemSchema(BaseModel):
    id: int
    uuid: str
    name: str
    year: int
    time: int
    imdb: float
    votes: int
    meta_score: Optional[float] = None
    gross: Optional[float] = None
    description: str
    price: float
    certification_id: int

    model_config = ConfigDict(from_attributes=True)


class MovieListResponseSchema(BaseModel):
    movies: List[MovieListItemSchema]
    total_count: int

    model_config = ConfigDict(from_attributes=True)


class MovieCreateSchema(BaseModel):
    uuid: UUID
    name: str
    year: int
    time: int
    imdb: float
    votes: int
    meta_score: Optional[float]
    gross: Optional[float]
    description: str
    price: float
    certification_id: int
    genres: List[int]
    directors: List[int]
    stars: List[int]

    model_config = ConfigDict(from_attributes=True)

class MovieUpdateSchema(BaseModel):
    name: Optional[str]
    year: Optional[int]
    time: Optional[int]
    imdb: Optional[float]
    votes: Optional[int]
    meta_score: Optional[float]
    gross: Optional[float]
    description: Optional[str]
    price: Optional[float]
    certification_id: Optional[int]
    genres: Optional[List[int]]
    directors: Optional[List[int]]
    stars: Optional[List[int]]

    model_config = ConfigDict(from_attributes=True)

class GenreCreateSchema(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True)

class GenreUpdateSchema(BaseModel):
    name: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class StarCreateSchema(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True)

class StarUpdateSchema(BaseModel):
    name: Optional[str]

    model_config = ConfigDict(from_attributes=True)
