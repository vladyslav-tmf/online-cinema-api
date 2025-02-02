from fastapi import FastAPI

from app.routes.accounts import router as accounts_router
from app.routes.movie_metadata import router as movie_metadata_router
from app.routes.movies import router as movie_router
from app.routes.profiles import router as profiles_router
from app.routes.shopping_carts import router as shopping_carts_router

app = FastAPI()

app.include_router(accounts_router, prefix="/accounts", tags=["accounts"])
app.include_router(profiles_router, prefix="/profiles", tags=["profiles"])
app.include_router(movie_router, prefix="/movies", tags=["movies"])
app.include_router(
    movie_metadata_router, prefix="/movie-metadata", tags=["movie-metadata"]
)
app.include_router(shopping_carts_router, prefix="/cart", tags=["shopping-carts"])
