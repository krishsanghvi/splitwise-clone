from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from supabase import Client
from app.database import get_supabase
from app.crud.groups import get_group_crud, GroupCRUD
from app.schemas.groups import Groups

router = APIRouter()


@router.post("/", response_model=Groups, status_code=status.HTTP_201_CREATED)
async def create_group(
    created_by: str,
    name: str,
    description: Optional[str] = None,
    invite_code: Optional[str] = None,
    supabase: Client = Depends(get_supabase),
):
    """
    Create a new group

    - **created_by**: User ID who is creating the group
    - **name**: Group name (required)
    - **description**: Group description (optional)
    - **invite_code**: Custom invite code (optional)
    """
    group_crud = get_group_crud(supabase)

    # Check if invite code is already in use
    if invite_code:
        existing_group = await group_crud.get_group_by_invite_code(invite_code)
        if existing_group:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invite code already in use"
            )

    group = await group_crud.create_group(created_by, name, description, invite_code)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create group"
        )

    return group


@router.get("/{group_id}", response_model=Groups)
async def get_group(
    group_id: str,
    supabase: Client = Depends(get_supabase),
):
    """Get group by ID"""
    group_crud = get_group_crud(supabase)
    group = await group_crud.get_group_by_id(group_id)

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )

    return group


@router.get("/invite/{invite_code}", response_model=Groups)
async def get_group_by_invite_code(
    invite_code: str,
    supabase: Client = Depends(get_supabase)
):
    """Get group by invite code"""
    group_crud = get_group_crud(supabase)
    group = await group_crud.get_group_by_invite_code(invite_code)

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    return group


@router.get("/search", response_model=List[Groups])
async def search_groups(
    search_term: str,
    limit: int = Query(20, ge=1, le=100),
    supabase: Client = Depends(get_supabase)
):
    """Search groups by name or description"""
    group_crud = get_group_crud(supabase)
    return await group_crud.search_groups(search_term, limit)


@router.get("/", response_model=List[Groups])
async def get_all_groups(
    limit: int = Query(
        50, ge=1, le=100, description="Number of groups to return"),
    offset: int = Query(0, ge=0, description="Number of groups to skip"),
    supabase: Client = Depends(get_supabase)
):
    """List all active groups with pagination

    - **limit**: Maximum number of groups to return (1-100)
    - **offset**: Number of groups to skip for pagination
    """
    group_crud = get_group_crud(supabase)
    groups = await group_crud.get_all_groups(limit=limit, offset=offset)

    return groups


@router.get("/user/{user_id}", response_model=List[Groups])
async def get_groups_by_user(
    user_id: str,
    limit: int = Query(
        50, ge=1, le=100, description="Number of groups to return"),
    offset: int = Query(0, ge=0, description="Number of groups to skip"),
    supabase: Client = Depends(get_supabase)
):
    """Get all groups created by a specific user

    - **user_id**: ID of the user who created the groups
    - **limit**: Maximum number of groups to return (1-100)
    - **offset**: Number of groups to skip for pagination
    """
    group_crud = get_group_crud(supabase)
    groups = await group_crud.get_groups_by_user(user_id, limit=limit, offset=offset)

    return groups


@router.put("/{group_id}", response_model=Groups)
async def update_group(
    group_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    invite_code: Optional[str] = None,
    is_active: Optional[bool] = None,
    supabase: Client = Depends(get_supabase)
):
    """Update group information
    - **name**: New group name (optional)
    - **description**: New group description (optional)  
    - **invite_code**: New invite code (optional)
    - **is_active**: Active status (optional)

    Only provided fields will be updated.
    """
    group_crud = get_group_crud(supabase)

    # Check if group exists
    existing_group = await group_crud.get_group_by_id(group_id)
    if not existing_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )

    # Check if invite code is already in use
    if invite_code:
        existing_group_with_code = await group_crud.get_group_by_invite_code(invite_code)
        if existing_group_with_code and existing_group_with_code.id != group_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invite code already in use"
            )

    updated_group = await group_crud.update_group(group_id, name, description, invite_code, is_active)

    if not updated_group:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update group"
        )

    return updated_group


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group_id: str,
    supabase: Client = Depends(get_supabase)
):
    """Delete group (soft delete)"""
    group_crud = get_group_crud(supabase)
    existing_group = await group_crud.get_group_by_id(group_id)
    if not existing_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )

    success = await group_crud.delete_group(group_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete group"
        )
