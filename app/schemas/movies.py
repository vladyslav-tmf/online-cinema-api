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
    meta_score: Optional[float]
    gross: Optional[float]
    description: str
    price: float
    certification: CertificationSchema
    genres: List[GenreSchema]
    directors: List[DirectorSchema]
    stars: List[StarSchema]

    model_config = ConfigDict(from_attributes=True)


class PaginationSchema(BaseModel):
    movies: List[MovieSchema]
    prev_page: Optional[str]
    next_page: Optional[str]
    total_items: int
    total_pages: int

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

