from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class GenreSchema(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True
    }

class StarSchema(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True
    }

class DirectorSchema(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True
    }

class CertificationSchema(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True
    }

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

    model_config = {
        "from_attributes": True
    }