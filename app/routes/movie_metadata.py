from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.dependencies import get_current_user
from app.database.models.accounts import UserGroupEnum, UserModel
from app.database.models.movies import (
    CertificationModel,
    DirectorModel,
    GenreModel,
    StarModel,
)
from app.database.session import get_db
from app.schemas.movies import (
    CertificationSchema,
    DirectorSchema,
    GenreSchema,
    StarSchema,
)

router = APIRouter()


@router.get("/certifications/", response_model=list[CertificationSchema])
def get_certifications(db: Session = Depends(get_db)):
    return db.query(CertificationModel).all()


@router.post("/certifications/", response_model=CertificationSchema)
def create_certification(
    name: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    if not current_user.has_group(UserGroupEnum.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create certifications",
        )

    if db.query(CertificationModel).filter(CertificationModel.name == name).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Certification with this name already exists",
        )

    certification = CertificationModel(name=name)
    db.add(certification)
    db.commit()
    db.refresh(certification)
    return certification


@router.get("/genres/", response_model=list[GenreSchema])
def get_genres(db: Session = Depends(get_db)):
    return db.query(GenreModel).all()


@router.post("/genres/", response_model=GenreSchema, summary="Create a new genre")
def create_genre(
    name: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    if not current_user.has_group(UserGroupEnum.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create genres",
        )

    if db.query(GenreModel).filter(GenreModel.name == name).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Genre with this name already exists",
        )

    new_genre = GenreModel(name=name)
    db.add(new_genre)
    db.commit()
    db.refresh(new_genre)
    return new_genre


@router.put("/genres/{genre_id}", response_model=GenreSchema, summary="Update a genre")
def update_genre(
    genre_id: int,
    name: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    if not current_user.has_group(UserGroupEnum.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create genres",
        )

    existing_genre = db.query(GenreModel).filter(GenreModel.id == genre_id).first()
    if not existing_genre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Genre not found"
        )

    existing_genre.name = name
    db.commit()
    db.refresh(existing_genre)
    return existing_genre


@router.get("/directors/", response_model=list[DirectorSchema])
def get_directors(db: Session = Depends(get_db)):
    return db.query(DirectorModel).all()


@router.post("/directors/", response_model=DirectorSchema)
def create_director(
    name: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    if not current_user.has_group(UserGroupEnum.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create directors",
        )

    if db.query(DirectorModel).filter(DirectorModel.name == name).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Director with this name already exists",
        )

    director = DirectorModel(name=name)
    db.add(director)
    db.commit()
    db.refresh(director)
    return director


@router.get("/stars/", response_model=list[StarSchema])
def get_stars(db: Session = Depends(get_db)):
    return db.query(StarModel).all()


@router.post(
    "/stars/",
    response_model=StarSchema,
    summary="Create a new actor",
    status_code=status.HTTP_201_CREATED,
)
def create_star(
    name: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    if not current_user.has_group(UserGroupEnum.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create stars",
        )

    if db.query(StarModel).filter(StarModel.name == name).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Star with this name already exists",
        )

    new_star = StarModel(name=name)
    db.add(new_star)
    db.commit()
    db.refresh(new_star)
    return new_star


@router.put("/stars/{star_id}", response_model=StarSchema, summary="Update an actor")
def update_star(
    star_id: int,
    name: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    if not current_user.has_group(UserGroupEnum.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create stars",
        )

    existing_star = db.query(StarModel).filter(StarModel.id == star_id).first()
    if not existing_star:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Actor not found"
        )

    existing_star.name = name
    db.commit()
    db.refresh(existing_star)
    return existing_star
