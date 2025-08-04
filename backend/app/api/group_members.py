from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from supabase import Client
from app.database import get_supabase
from app.crud.group_members import get_group_member_crud, GroupMemberCRUD
from app.schemas.group_members import GroupMembers

router = APIRouter()


@router.post("/", response_model=GroupMembers, status_code=status.HTTP_201_CREATED)
async def add_member_to_group(
    group_id: str,
    user_id: str,
    role: str = "member",
    supabase: Client = Depends(get_supabase),
):
    """
    Add a new member to a group

    - **group_id**: ID of the group
    - **user_id**: ID of the user to add
    - **role**: Role of the member (member, admin, owner)
    """
    member_crud = get_group_member_crud(supabase)

    # Check if user is already a member
    existing_member = await member_crud.get_member_by_user_and_group(group_id, user_id)
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this group"
        )

    member = await member_crud.add_member(group_id, user_id, role)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add member to group"
        )

    return member


@router.get("/member/{member_id}", response_model=GroupMembers)
async def get_member(
    member_id: str,
    supabase: Client = Depends(get_supabase),
):
    """Get member by ID"""
    member_crud = get_group_member_crud(supabase)
    member = await member_crud.get_member_by_id(member_id)

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    return member


@router.get("/group/{group_id}/member/{user_id}", response_model=GroupMembers)
async def get_member_by_user_and_group(
    group_id: str,
    user_id: str,
    supabase: Client = Depends(get_supabase)
):
    """Get member by group ID and user ID"""
    member_crud = get_group_member_crud(supabase)
    member = await member_crud.get_member_by_user_and_group(group_id, user_id)

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    return member


@router.get("/group/{group_id}/members", response_model=List[GroupMembers])
async def get_group_members(
    group_id: str,
    limit: int = Query(50, ge=1, le=100, description="Number of members to return"),
    offset: int = Query(0, ge=0, description="Number of members to skip"),
    supabase: Client = Depends(get_supabase)
):
    """Get all members of a group

    - **group_id**: ID of the group
    - **limit**: Maximum number of members to return (1-100)
    - **offset**: Number of members to skip for pagination
    """
    member_crud = get_group_member_crud(supabase)
    members = await member_crud.get_group_members(group_id, limit=limit, offset=offset)

    return members


@router.get("/user/{user_id}/groups", response_model=List[GroupMembers])
async def get_user_groups(
    user_id: str,
    limit: int = Query(50, ge=1, le=100, description="Number of groups to return"),
    offset: int = Query(0, ge=0, description="Number of groups to skip"),
    supabase: Client = Depends(get_supabase)
):
    """Get all groups a user is a member of

    - **user_id**: ID of the user
    - **limit**: Maximum number of groups to return (1-100)
    - **offset**: Number of groups to skip for pagination
    """
    member_crud = get_group_member_crud(supabase)
    groups = await member_crud.get_user_groups(user_id, limit=limit, offset=offset)

    return groups


@router.get("/group/{group_id}/admins", response_model=List[GroupMembers])
async def get_group_admins(
    group_id: str,
    supabase: Client = Depends(get_supabase)
):
    """Get all admins/owners of a group"""
    member_crud = get_group_member_crud(supabase)
    admins = await member_crud.get_group_admins(group_id)

    return admins


@router.put("/member/{member_id}/role", response_model=GroupMembers)
async def update_member_role(
    member_id: str,
    role: str,
    supabase: Client = Depends(get_supabase)
):
    """Update member role
    - **role**: New role for the member (member, admin, owner)
    """
    member_crud = get_group_member_crud(supabase)

    # Check if member exists
    existing_member = await member_crud.get_member_by_id(member_id)
    if not existing_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    # Validate role
    valid_roles = ["member", "admin", "owner"]
    if role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )

    updated_member = await member_crud.update_member_role(member_id, role)

    if not updated_member:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update member role"
        )

    return updated_member


@router.delete("/member/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    member_id: str,
    supabase: Client = Depends(get_supabase)
):
    """Remove member from group"""
    member_crud = get_group_member_crud(supabase)
    existing_member = await member_crud.get_member_by_id(member_id)
    if not existing_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    success = await member_crud.remove_member(member_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove member"
        )


@router.delete("/group/{group_id}/member/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member_from_group(
    group_id: str,
    user_id: str,
    supabase: Client = Depends(get_supabase)
):
    """Remove member from group by group ID and user ID"""
    member_crud = get_group_member_crud(supabase)
    
    # Check if member exists
    existing_member = await member_crud.get_member_by_user_and_group(group_id, user_id)
    if not existing_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    success = await member_crud.remove_member_by_user_and_group(group_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove member"
        )


@router.get("/group/{group_id}/member/{user_id}/check", response_model=dict)
async def check_membership(
    group_id: str,
    user_id: str,
    supabase: Client = Depends(get_supabase)
):
    """Check if user is a member of the group"""
    member_crud = get_group_member_crud(supabase)
    is_member = await member_crud.is_member(group_id, user_id)
    is_admin = await member_crud.is_admin(group_id, user_id)

    return {
        "is_member": is_member,
        "is_admin": is_admin
    }