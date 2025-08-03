from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from supabase import Client
from app.database import get_supabase
from app.crud.users import get_user_crud, UserCRUD
from app.schemas.users import User
import uuid

router = APIRouter()


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    email: str,
    full_name: str,
    timezone: str = "UTC",
    supabase: Client = Depends(get_supabase),
):
    """
    Create a new user

    - **email**: User's email address (must be unique)
    - **full_name**: User's display name
    - **timezone**: User's timezone (defaults to UTC)
    """
    user_crud = get_user_crud(supabase)

    # Check if user already exists
    existing_user = await user_crud.get_user_by_email(email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    user = await user_crud.create_user(email, full_name, timezone)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

    return user


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: str,
    supabase: Client = Depends(get_supabase),
):
    """Get user by ID"""
    user_crud = get_user_crud(supabase)
    user = await user_crud.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.get("/", response_model=List[User])
async def get_all_users(supabase: Client = Depends(get_supabase)):
    """Get all users"""
    user_crud = get_user_crud(supabase)
    list_of_users = await user_crud.get_all_users()

    return list_of_users
