from fastapi import FastAPI

from routes.accounts import router as accounts_router
from routes.movie_metadata import router as movie_metadata_router
from routes.movies import router as movie_router
from routes.profiles import router as profiles_router

app = FastAPI()

app.include_router(accounts_router, prefix="/accounts", tags=["accounts"])
app.include_router(profiles_router, prefix="/profiles", tags=["profiles"])
app.include_router(movie_router, prefix="/movies", tags=["movies"])
app.include_router(
    movie_metadata_router, prefix="/movie-metadata", tags=["movie-metadata"]
)
