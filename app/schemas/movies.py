from pydantic import BaseModel, ConfigDict, Field
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
    meta_score: float | None = None
    gross: float | None = None
    description: str
    price: float
    certification_id: int

    model_config = ConfigDict(from_attributes=True)


class MovieListResponseSchema(BaseModel):
    movies: list[MovieListItemSchema]
    total_count: int

    model_config = ConfigDict(from_attributes=True)


class MovieCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    year: int = Field(..., ge=1888, le=2100)
    time: int = Field(..., ge=1)
    imdb: float = Field(..., ge=0, le=10)
    votes: int = Field(..., ge=0)
    meta_score: float | None = Field(None, ge=0, le=100)
    gross: float | None = None
    description: str = Field(..., min_length=1)
    price: float = Field(..., ge=0)
    certification_id: int
    genre_ids: list[int]
    director_ids: list[int]
    star_ids: list[int]

    model_config = ConfigDict(from_attributes=True)

class MovieUpdateSchema(MovieCreateSchema):
    name: str | None = Field(None, min_length=1, max_length=255)
    year: int | None = Field(None, ge=1888, le=2100)
    time: int | None = Field(None, ge=1)
    imdb: float | None = Field(None, ge=0, le=10)
    votes: int | None = Field(None, ge=0)
    meta_score: float | None = Field(None, ge=0, le=100)
    gross: float | None = None
    description: str | None = Field(None, min_length=1)
    price: float | None = Field(None, ge=0)
    certification_id: int | None = None
    genre_ids: list[int] | None = None
    director_ids: list[int] | None = None
    star_ids: list[int] | None = None

class GenreCreateSchema(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True)

class GenreUpdateSchema(BaseModel):
    name: str | None = None

    model_config = ConfigDict(from_attributes=True)

class StarCreateSchema(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True)

class StarUpdateSchema(BaseModel):
    name: str | None = None

    model_config = ConfigDict(from_attributes=True)
