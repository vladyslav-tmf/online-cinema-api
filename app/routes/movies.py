from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models.movies import MovieModel
from app.schemas.movies import (
    PaginationSchema,
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

