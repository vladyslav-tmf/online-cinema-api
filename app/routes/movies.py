from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload

from app.database.models.movies import (
    CertificationModel,
    DirectorModel,
    GenreModel,
    MovieModel,
    StarModel,
)
from app.database.session import get_db
from app.schemas.movies import (
    MovieCreateSchema,
    MovieSchema,
    MovieUpdateSchema,
    PaginationSchema,
)
from config.dependencies import get_current_user
from database.models.accounts import UserGroupEnum, UserModel
from database.models.movie_interactions import (
    CommentLikeModel,
    LikeTypeEnum,
    MovieCommentModel,
    MovieFavoriteModel,
    MovieLikeModel,
    MovieRatingModel,
)
from exceptions.movies import (
    CommentAlreadyLikedError,
    CommentNotFoundError,
    MovieAlreadyFavoritedError,
    MovieAlreadyLikedError,
    MovieAlreadyRatedError,
    MovieNotFoundError,
)
from schemas.movie_interactions import (
    CommentLikeResponseSchema,
    MovieCommentCreateSchema,
    MovieCommentResponseSchema,
    MovieFavoriteResponseSchema,
    MovieLikeCreateSchema,
    MovieLikeResponseSchema,
    MovieRatingCreateSchema,
    MovieRatingResponseSchema,
)

router = APIRouter()

SORT_FIELDS = {"name", "year", "imdb", "votes", "meta_score", "price"}
SORT_ORDERS = {"asc", "desc"}


@router.get(
    "/",
    response_model=PaginationSchema,
    summary="Get a paginated list of movies",
    description=(
        "<h3>This endpoint retrieves a paginated list of movies from the database. "
        "Clients can specify the `page` number and the number of items per page using "
        "`per_page`. The response includes details about the movies, total pages, "
        "and total items, along with links to the previous "
        "and next pages if applicable.</h3>"
    ),
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "No movies found.",
            "content": {
                "application/json": {"example": {"detail": "No movies found."}}
            },
        }
    },
)
def get_movies(
    page: int = Query(1, ge=1, description="Page number (1-based index)"),
    per_page: int = Query(10, ge=1, le=20, description="Number of items per page"),
    db: Session = Depends(get_db),
    current_user: UserModel | None = Depends(get_current_user),
    search: str | None = None,
    year: int | None = None,
    genre_id: int | None = None,
    director_id: int | None = None,
    star_id: int | None = None,
    certification_id: int | None = None,
    sort_by: str = Query("name"),
    sort_order: str = Query("asc"),
) -> PaginationSchema:
    if sort_by not in SORT_FIELDS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sort field. Must be one of: {', '.join(SORT_FIELDS)}",
        )
    if sort_order not in SORT_ORDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sort order. Must be one of: {', '.join(SORT_ORDERS)}",
        )

    query = (
        db.query(MovieModel)
        .options(
            joinedload(MovieModel.certification),
            joinedload(MovieModel.genres),
            joinedload(MovieModel.directors),
            joinedload(MovieModel.stars),
            joinedload(MovieModel.likes),
            joinedload(MovieModel.favorited_by),
            joinedload(MovieModel.ratings),
        )
        .order_by(
            getattr(MovieModel, sort_by).desc()
            if sort_order == "desc"
            else getattr(MovieModel, sort_by)
        )
    )

    filters = []
    if search:
        filters.append(MovieModel.name.ilike(f"%{search}%"))
    if year:
        filters.append(MovieModel.year == year)
    if genre_id:
        query = query.join(MovieModel.genres)
        filters.append(GenreModel.id == genre_id)
    if director_id:
        query = query.join(MovieModel.directors)
        filters.append(DirectorModel.id == director_id)
    if star_id:
        query = query.join(MovieModel.stars)
        filters.append(StarModel.id == star_id)
    if certification_id:
        filters.append(MovieModel.certification_id == certification_id)

    if filters:
        query = query.filter(and_(*filters))

    total_items = query.count()
    total_pages = (total_items + per_page - 1) // per_page
    query = query.offset((page - 1) * per_page).limit(per_page)
    movies = query.all()

    if not movies:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No movies found."
        )

    if current_user:
        for movie in movies:
            movie.likes_count = sum(
                1 for like in movie.likes if like.like_type == LikeTypeEnum.LIKE
            )
            movie.dislikes_count = sum(
                1 for like in movie.likes if like.like_type == LikeTypeEnum.DISLIKE
            )
            movie.favorites_count = len(movie.favorited_by)
            movie.comments_count = len(movie.comments)

            movie_ratings = [rating.rating for rating in movie.ratings]
            movie.average_rating = (
                sum(movie_ratings) / len(movie_ratings) if movie_ratings else None
            )

            user_like = next(
                (like for like in movie.likes if like.user_id == current_user.id), None
            )
            movie.is_liked_by_user = (
                user_like.like_type == LikeTypeEnum.LIKE if user_like else False
            )
            movie.is_disliked_by_user = (
                user_like.like_type == LikeTypeEnum.DISLIKE if user_like else False
            )
            movie.is_favorited_by_user = any(
                favorite.user_id == current_user.id for favorite in movie.favorited_by
            )
            user_rating = next(
                (
                    rating.rating
                    for rating in movie.ratings
                    if rating.user_id == current_user.id
                ),
                None,
            )
            movie.user_rating = user_rating

    prev_page = f"/movies?page={page - 1}" if page > 1 else None
    next_page = f"/movies?page={page + 1}" if page < total_pages else None

    return PaginationSchema(
        movies=movies,
        prev_page=prev_page,
        next_page=next_page,
        total_items=total_items,
        total_pages=total_pages,
    )


@router.get("/{movie_id}", response_model=MovieSchema)
def get_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel | None = Depends(get_current_user),
):
    movie = (
        db.query(MovieModel)
        .options(
            joinedload(MovieModel.certification),
            joinedload(MovieModel.genres),
            joinedload(MovieModel.directors),
            joinedload(MovieModel.stars),
            joinedload(MovieModel.likes),
            joinedload(MovieModel.favorited_by),
            joinedload(MovieModel.ratings),
        )
        .filter(MovieModel.id == movie_id)
        .first()
    )

    if not movie:
        raise MovieNotFoundError()

    if current_user:
        movie.likes_count = sum(
            1 for like in movie.likes if like.like_type == LikeTypeEnum.LIKE
        )
        movie.dislikes_count = sum(
            1 for like in movie.likes if like.like_type == LikeTypeEnum.DISLIKE
        )
        movie.favorites_count = len(movie.favorited_by)
        movie.comments_count = len(movie.comments)

        movie_ratings = [rating.rating for rating in movie.ratings]
        movie.average_rating = (
            sum(movie_ratings) / len(movie_ratings) if movie_ratings else None
        )

        user_like = next(
            (like for like in movie.likes if like.user_id == current_user.id), None
        )
        movie.is_liked_by_user = (
            user_like.like_type == LikeTypeEnum.LIKE if user_like else False
        )
        movie.is_disliked_by_user = (
            user_like.like_type == LikeTypeEnum.DISLIKE if user_like else False
        )
        movie.is_favorited_by_user = any(
            favorite.user_id == current_user.id for favorite in movie.favorited_by
        )
        user_rating = next(
            (
                rating.rating
                for rating in movie.ratings
                if rating.user_id == current_user.id
            ),
            None,
        )
        movie.user_rating = user_rating

    return movie


@router.post(
    "/",
    response_model=MovieSchema,
    summary="Create a new movie",
    responses={
        status.HTTP_201_CREATED: {
            "description": "Movie created successfully.",
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid input.",
            "content": {
                "application/json": {"example": {"detail": "Invalid input data."}}
            },
        },
    },
    status_code=status.HTTP_201_CREATED,
)
def create_movie(
    movie_data: MovieCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    if not current_user.has_group(UserGroupEnum.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create movies",
        )

    certification = (
        db.query(CertificationModel)
        .filter(CertificationModel.id == movie_data.certification_id)
        .first()
    )
    if not certification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certification not found",
        )

    genres = db.query(GenreModel).filter(GenreModel.id.in_(movie_data.genre_ids)).all()
    if len(genres) != len(movie_data.genre_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Some genres were not found",
        )

    directors = (
        db.query(DirectorModel)
        .filter(DirectorModel.id.in_(movie_data.director_ids))
        .all()
    )
    if len(directors) != len(movie_data.director_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Some directors were not found",
        )

    stars = db.query(StarModel).filter(StarModel.id.in_(movie_data.star_ids)).all()
    if len(stars) != len(movie_data.star_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Some stars were not found",
        )

    new_movie = MovieModel(
        name=movie_data.name,
        year=movie_data.year,
        time=movie_data.time,
        imdb=movie_data.imdb,
        votes=movie_data.votes,
        meta_score=movie_data.meta_score,
        gross=movie_data.gross,
        description=movie_data.description,
        price=movie_data.price,
        certification_id=movie_data.certification_id,
        genres=genres,
        directors=directors,
        stars=stars,
    )

    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)

    return new_movie


@router.put("/{movie_id}", response_model=MovieSchema, summary="Update a movie")
def update_movie(
    movie_id: int,
    movie_data: MovieUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    if not current_user.has_group(UserGroupEnum.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can update movies",
        )

    movie = db.get(MovieModel, movie_id)
    if not movie:
        raise MovieNotFoundError()

    if not movie_data.certification_id:
        certification = (
            db.query(CertificationModel)
            .filter(CertificationModel.id == movie_data.certification_id)
            .first()
        )
        if not certification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Certification not found",
            )
        movie.certification_id = movie_data.certification_id

    if not movie_data.genre_ids:
        genres = (
            db.query(GenreModel).filter(GenreModel.id.in_(movie_data.genre_ids)).all()
        )
        if len(genres) != len(movie_data.genre_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Some genres were not found",
            )
        movie.genres = genres

    if not movie_data.director_ids:
        directors = (
            db.query(DirectorModel)
            .filter(DirectorModel.id.in_(movie_data.director_ids))
            .all()
        )
        if len(directors) != len(movie_data.director_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Some directors were not found",
            )
        movie.directors = directors

    if not movie_data.star_ids:
        stars = db.query(StarModel).filter(StarModel.id.in_(movie_data.star_ids)).all()
        if len(stars) != len(movie_data.star_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Some stars were not found",
            )
        movie.stars = stars

    for field, value in movie_data.model_dump(exclude_unset=True).items():
        if field not in {"certification_id", "genre_ids", "director_ids", "star_ids"}:
            setattr(movie, field, value)

    db.commit()
    db.refresh(movie)

    return movie


@router.delete(
    "/{movie_id}", summary="Delete a movie", status_code=status.HTTP_204_NO_CONTENT
)
def delete_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> dict[str, str]:
    if not current_user.has_group(UserGroupEnum.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete movies",
        )

    movie = db.get(MovieModel, movie_id)
    if not movie:
        raise MovieNotFoundError()

    db.delete(movie)
    db.commit()
    return {"message": "Movie deleted successfully"}


@router.post("/{movie_id}/like", response_model=MovieLikeResponseSchema)
def like_movie(
    movie_id: int,
    like_data: MovieLikeCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    movie = db.get(MovieModel, movie_id)
    if not movie:
        raise MovieNotFoundError()

    existing_like = (
        db.query(MovieLikeModel)
        .filter(
            MovieLikeModel.movie_id == movie_id,
            MovieLikeModel.user_id == current_user.id,
        )
        .first()
    )

    if existing_like:
        if existing_like.like_type == like_data.like_type:
            raise MovieAlreadyLikedError()
        db.delete(existing_like)
        db.commit()

    like = MovieLikeModel(
        user_id=current_user.id,
        movie_id=movie_id,
        like_type=like_data.like_type,
    )
    db.add(like)
    db.commit()
    db.refresh(like)
    return like


@router.delete("/{movie_id}/like", status_code=status.HTTP_204_NO_CONTENT)
def remove_movie_like(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    like = (
        db.query(MovieLikeModel)
        .filter(
            MovieLikeModel.movie_id == movie_id,
            MovieLikeModel.user_id == current_user.id,
        )
        .first()
    )
    if like:
        db.delete(like)
        db.commit()


@router.post("/{movie_id}/favorite", response_model=MovieFavoriteResponseSchema)
def add_to_favorites(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    movie = db.get(MovieModel, movie_id)
    if not movie:
        raise MovieNotFoundError()

    existing_favorite = (
        db.query(MovieFavoriteModel)
        .filter(
            MovieFavoriteModel.movie_id == movie_id,
            MovieFavoriteModel.user_id == current_user.id,
        )
        .first()
    )

    if existing_favorite:
        raise MovieAlreadyFavoritedError()

    favorite = MovieFavoriteModel(
        user_id=current_user.id,
        movie_id=movie_id,
    )
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return favorite


@router.delete("/{movie_id}/favorite", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_favorites(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    favorite = (
        db.query(MovieFavoriteModel)
        .filter(
            MovieFavoriteModel.movie_id == movie_id,
            MovieFavoriteModel.user_id == current_user.id,
        )
        .first()
    )
    if favorite:
        db.delete(favorite)
        db.commit()


@router.post("/{movie_id}/rating", response_model=MovieRatingResponseSchema)
def rate_movie(
    movie_id: int,
    rating_data: MovieRatingCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    movie = db.get(MovieModel, movie_id)
    if not movie:
        raise MovieNotFoundError()

    existing_rating = (
        db.query(MovieRatingModel)
        .filter(
            MovieRatingModel.movie_id == movie_id,
            MovieRatingModel.user_id == current_user.id,
        )
        .first()
    )

    if existing_rating:
        raise MovieAlreadyRatedError()

    rating = MovieRatingModel(
        user_id=current_user.id,
        movie_id=movie_id,
        rating=rating_data.rating,
    )
    db.add(rating)
    db.commit()
    db.refresh(rating)
    return rating


@router.delete("/{movie_id}/rating", status_code=status.HTTP_204_NO_CONTENT)
def remove_movie_rating(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    rating = (
        db.query(MovieRatingModel)
        .filter(
            MovieRatingModel.movie_id == movie_id,
            MovieRatingModel.user_id == current_user.id,
        )
        .first()
    )
    if rating:
        db.delete(rating)
        db.commit()


@router.post("/{movie_id}/comments", response_model=MovieCommentResponseSchema)
def create_comment(
    movie_id: int,
    comment_data: MovieCommentCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    movie = db.get(MovieModel, movie_id)
    if not movie:
        raise MovieNotFoundError()

    if comment_data.parent_id:
        parent_comment = db.get(MovieCommentModel, comment_data.parent_id)
        if not parent_comment or parent_comment.movie_id != movie_id:
            raise CommentNotFoundError()

    comment = MovieCommentModel(
        user_id=current_user.id,
        movie_id=movie_id,
        parent_id=comment_data.parent_id,
        text=comment_data.text,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    comment.likes_count = 0
    comment.is_liked_by_user = False

    return comment


@router.get("/{movie_id}/comments", response_model=list[MovieCommentResponseSchema])
def get_movie_comments(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    movie = db.get(MovieModel, movie_id)
    if not movie:
        raise MovieNotFoundError()

    comments = (
        db.query(MovieCommentModel).filter(MovieCommentModel.movie_id == movie_id).all()
    )

    for comment in comments:
        comment.likes_count = len(comment.likes)
        comment.is_liked_by_user = any(
            like.user_id == current_user.id for like in comment.likes
        )

    return comments


@router.post(
    "/{movie_id}/comments/{comment_id}/like",
    response_model=CommentLikeResponseSchema,
)
def like_comment(
    movie_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    comment = db.get(MovieCommentModel, comment_id)
    if not comment or comment.movie_id != movie_id:
        raise CommentNotFoundError()

    existing_like = (
        db.query(CommentLikeModel)
        .filter(
            CommentLikeModel.comment_id == comment_id,
            CommentLikeModel.user_id == current_user.id,
        )
        .first()
    )

    if existing_like:
        raise CommentAlreadyLikedError()

    like = CommentLikeModel(
        user_id=current_user.id,
        comment_id=comment_id,
    )
    db.add(like)
    db.commit()
    db.refresh(like)
    return like


@router.delete(
    "/{movie_id}/comments/{comment_id}/like",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_comment_like(
    movie_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    comment = db.get(MovieCommentModel, comment_id)
    if not comment or comment.movie_id != movie_id:
        raise CommentNotFoundError()

    like = (
        db.query(CommentLikeModel)
        .filter(
            CommentLikeModel.comment_id == comment_id,
            CommentLikeModel.user_id == current_user.id,
        )
        .first()
    )
    if like:
        db.delete(like)
        db.commit()
