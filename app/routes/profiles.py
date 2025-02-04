from typing import cast

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import HttpUrl
from sqlalchemy.orm import Session

from app.config.dependencies import get_current_user, get_s3_storage_client
from app.database.models.accounts import (
    GenderEnum,
    UserGroupEnum,
    UserModel,
    UserProfileModel,
)
from app.database.session import get_db
from app.exceptions.storage import S3FileUploadError
from app.schemas.profiles import ProfileCreateSchema, ProfileResponseSchema
from app.storages.interfaces import S3StorageInterface

router = APIRouter()


@router.post(
    "/users/{user_id}/profile/",
    response_model=ProfileResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a user profile",
    description="Creates a new profile for a user, including personal information and avatar. Only admins or the user themselves can create a profile.",
    responses={
        201: {
            "description": "Profile created successfully",
            },
        400: {
            "description": "Bad request: The user already has a profile.",
        },
        401: {
            "description": "Unauthorized: User not found or not active.",
        },
        403: {
            "description": "Forbidden: You don't have permission to edit this profile.",
        },
        500: {
            "description": "Internal server error: Failed to upload avatar to S3.",
        },
    },
)
def create_profile(
    user_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
    s3_client: S3StorageInterface = Depends(get_s3_storage_client),
    profile_data: ProfileCreateSchema = Depends(ProfileCreateSchema.from_form),
) -> ProfileResponseSchema:
    if user_id != current_user.id:
        user_group = current_user.group

        if not user_group or user_group.name == UserGroupEnum.USER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to edit this profile.",
            )

    user = db.query(UserModel).filter_by(id=user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or not active.",
        )

    existing_profile = db.query(UserProfileModel).filter_by(user_id=user.id).first()
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a profile.",
        )

    avatar_bytes = profile_data.avatar.file.read()
    avatar_key = f"avatars/{user.id}_{profile_data.avatar.filename}"

    try:
        s3_client.upload_file(file_name=avatar_key, file_data=avatar_bytes)
    except S3FileUploadError as e:
        print(f"Error uploading avatar to S3: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload avatar. Please try again later.",
        )

    new_profile = UserProfileModel(
        user_id=cast(int, user.id),
        first_name=profile_data.first_name,
        last_name=profile_data.last_name,
        gender=cast(GenderEnum, profile_data.gender),
        date_of_birth=profile_data.date_of_birth,
        info=profile_data.info,
        avatar=avatar_key,
    )

    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    avatar_url = s3_client.get_file_url(new_profile.avatar)

    return ProfileResponseSchema(
        id=new_profile.id,
        user_id=new_profile.user_id,
        first_name=new_profile.first_name,
        last_name=new_profile.last_name,
        gender=new_profile.gender,
        date_of_birth=new_profile.date_of_birth,
        info=new_profile.info,
        avatar=cast(HttpUrl, avatar_url),
    )
