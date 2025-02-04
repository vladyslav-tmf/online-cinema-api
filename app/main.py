from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.init_db import init_user_groups
from app.database.session import SessionLocal
from app.routes.accounts import router as accounts_router
from app.routes.movie_metadata import router as movie_metadata_router
from app.routes.movies import router as movie_router
from app.routes.orders import router as order_router
from app.routes.payments import router as payments_router
from app.routes.profiles import router as profiles_router
from app.routes.shopping_carts import router as shopping_carts_router

app = FastAPI()


origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


if __name__ == "__main__":
    db = SessionLocal()
    try:
        init_user_groups(db)
    finally:
        db.close()


app.include_router(accounts_router, prefix="/accounts", tags=["accounts"])
app.include_router(profiles_router, prefix="/profiles", tags=["profiles"])
app.include_router(movie_router, prefix="/movies", tags=["movies"])
app.include_router(
    movie_metadata_router, prefix="/movie-metadata", tags=["movie-metadata"]
)
app.include_router(order_router, prefix="/orders", tags=["orders"])
app.include_router(shopping_carts_router, prefix="/cart", tags=["shopping-carts"])
app.include_router(payments_router, prefix="/payments", tags=["payments"])
