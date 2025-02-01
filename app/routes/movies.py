from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models.movies import MovieModel, GenreModel, StarModel
from app.schemas.movies import (
    PaginationSchema,
    MovieSchema,
    GenreSchema,
    StarSchema, MovieCreateSchema, MovieUpdateSchema, GenreCreateSchema,
    GenreUpdateSchema, StarCreateSchema, StarUpdateSchema,
)

router = APIRouter()

@router.get(
    "/movies/",
    response_model=PaginationSchema,
    summary="Get a paginated list of movies",
    description=(
            "<h3>This endpoint retrieves a paginated list of movies from the database. "
            "Clients can specify the `page` number and the number of items per page using `per_page`. "
            "The response includes details about the movies, total pages, and total items, "
            "along with links to the previous and next pages if applicable.</h3>"
    ),
    responses={
        404: {
            "description": "No movies found.",
            "content": {
                "application/json": {
                    "example": {"detail": "No movies found."}
                }
            },
        }
    }
)
def get_movies(
        page: int = Query(1, ge=1, description="Page number (1-based index)"),
        per_page: int = Query(10, ge=1, le=20,
                              description="Number of items per page"),
        db: Session = Depends(get_db),
) -> PaginationSchema:
    offset = (page - 1) * per_page

    query = db.query(MovieModel).order_by()  ###

    total_items = query.count()
    movies = query.offset(offset).limit(per_page).all()

    total_pages = (total_items + per_page - 1) // per_page

    if not movies:
        raise HTTPException(status_code=404, detail="No movies found.")

    return PaginationSchema(
        movies=movies,
        prev_page=f"/movies/?page={page - 1}&per_page={per_page}" if page > 1 else None,
        next_page=f"/movies/?page={page + 1}&per_page={per_page}" if page < total_pages else None,
        total_items=total_items,
        total_pages=total_pages
    )

@router.post("/movies/",
             response_model=MovieSchema,
             summary="Create a new movie",
             responses={
                 201: {
                     "description": "Movie created successfully.",
                 },
                 400: {
                     "description": "Invalid input.",
                     "content": {
                         "application/json": {
                             "example": {"detail": "Invalid input data."}
                         }
                     },
                 }
             },
             status_code=201
             )

def create_movie(movie: MovieCreateSchema, db: Session = Depends(get_db)):
    new_movie = MovieModel(**movie.dict())
    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)
    return new_movie

@router.put("/movies/{movie_id}", response_model=MovieSchema, summary="Update a movie")
def update_movie(movie_id: int, movie: MovieUpdateSchema, db: Session = Depends(get_db)):
    existing_movie = db.query(MovieModel).filter(MovieModel.id == movie_id).first()
    if not existing_movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    for key, value in movie.dict(exclude_unset=True).items():
        setattr(existing_movie, key, value)
    db.commit()
    db.refresh(existing_movie)
    return existing_movie

@router.delete("/movies/{movie_id}", summary="Delete a movie")
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(MovieModel).filter(MovieModel.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    db.delete(movie)
    db.commit()
    return {"message": "Movie deleted successfully"}


@router.post("/genres/", response_model=GenreSchema, summary="Create a new genre")
def create_genre(genre: GenreCreateSchema, db: Session = Depends(get_db)):
    new_genre = GenreModel(**genre.dict())
    db.add(new_genre)
    db.commit()
    db.refresh(new_genre)
    return new_genre

@router.put("/genres/{genre_id}", response_model=GenreSchema, summary="Update a genre")
def update_genre(genre_id: int, genre: GenreUpdateSchema, db: Session = Depends(get_db)):
    existing_genre = db.query(GenreModel).filter(GenreModel.id == genre_id).first()
    if not existing_genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    for key, value in genre.dict(exclude_unset=True).items():
        setattr(existing_genre, key, value)
    db.commit()
    db.refresh(existing_genre)
    return existing_genre


@router.post("/stars/", response_model=StarSchema, summary="Create a new actor")
def create_star(star: StarCreateSchema, db: Session = Depends(get_db)):
    new_star = StarModel(**star.dict())
    db.add(new_star)
    db.commit()
    db.refresh(new_star)
    return new_star

@router.put("/stars/{star_id}", response_model=StarSchema, summary="Update an actor")
def update_star(star_id: int, star: StarUpdateSchema, db: Session = Depends(get_db)):
    existing_star = db.query(StarModel).filter(StarModel.id == star_id).first()
    if not existing_star:
        raise HTTPException(status_code=404, detail="Actor not found")
    for key, value in star.dict(exclude_unset=True).items():
        setattr(existing_star, key, value)
    db.commit()
    db.refresh(existing_star)
    return existing_star
