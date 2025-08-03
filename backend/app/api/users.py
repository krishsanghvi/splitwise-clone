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


@router.get("/{email}", response_model=User)
async def get_user_by_email(
    email: str,
    supabase: Client = Depends(get_supabase)
):
    """Get user by email"""
    user_crud = get_user_crud(supabase)
    user = await user_crud.get_user_by_email(email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.get("/", response_model=List[User])
async def get_all_users(
    limit: int = Query(
        50, ge=1, le=100, description="Number of users to return"),
    offset: int = Query(0, ge=0, description="Number of users to skip"),
    supabase: Client = Depends(get_supabase)
):
    """List users with pagination

    - **limit**: Maximum number of users to return (1-100)
    - **offset**: Number of users to skip for pagination
    """
    user_crud = get_user_crud(supabase)
    list_of_users = await user_crud.get_all_users(limit=limit, offset=offset)

    return list_of_users


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    email: Optional[str] = None,
    full_name: Optional[str] = None,
    timezone: Optional[str] = None,
    supabase: Client = Depends(get_supabase)
):
    """Update user information
    - **email**: New email address (optional)
    - **full_name**: New display name (optional)  
    - **timezone**: New timezone (optional)

    Only provided fields will be updated.
    """
    user_crud = get_user_crud(supabase)

    # Check if user exists
    existing_user = await user_crud.get_user_by_id(user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if email is already in use
    if email:
        existing_user_with_email = await user_crud.get_user_by_email(email)
        if existing_user_with_email and existing_user_with_email.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )

    updated_user = await user_crud.update_user(user_id, email, full_name, timezone)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )

    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    supabase: Client = Depends(get_supabase)
):
    """Delete user"""
    user_crud = get_user_crud(supabase)
    existing_user = await user_crud.get_user_by_id(user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    success = await user_crud.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )


@router.get("/search", response_model=List[User])
async def search_users(
    search_term: str,
    limit: int = Query(
        20, ge=1, le=100, description="Number of users to return"),
    supabase: Client = Depends(get_supabase)
):
    """Search users by name or email"""
    user_crud = get_user_crud(supabase)
    users = await user_crud.search_users(search_term, limit)
    return users
