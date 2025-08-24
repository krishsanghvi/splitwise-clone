from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from supabase import Client

from app.database import get_supabase
from app.crud.settlements import get_settlements_crud, SettlementsCRUD
from app.schemas.settlements import Settlements

router = APIRouter()


@router.post("/", response_model=Settlements, status_code=status.HTTP_201_CREATED)
async def create_settlement(
    group_id: str,
    from_user: str,
    to_user: str,
    amount: str,
    method: str = "cash",
    reference_id: Optional[str] = None,
    notes: Optional[str] = None,
    supabase: Client = Depends(get_supabase),
):
    """
    Create a new settlement
    
    - **group_id**: ID of the group this settlement belongs to
    - **from_user**: ID of the user making the payment
    - **to_user**: ID of the user receiving the payment
    - **amount**: Amount of the settlement
    - **method**: Payment method (defaults to 'cash')
    - **reference_id**: Optional reference ID for the payment
    - **notes**: Optional notes about the settlement
    """
    settlements_crud = get_settlements_crud(supabase)
    
    # Validate that from_user and to_user are different
    if from_user == to_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="From user and to user cannot be the same"
        )
    
    settlement = await settlements_crud.create_settlement(
        group_id=group_id,
        from_user=from_user,
        to_user=to_user,
        amount=amount,
        method=method,
        reference_id=reference_id,
        notes=notes
    )
    
    if not settlement:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create settlement"
        )
    
    return settlement


@router.get("/{settlement_id}", response_model=Settlements)
async def get_settlement(
    settlement_id: str,
    supabase: Client = Depends(get_supabase),
):
    """Get settlement by ID"""
    settlements_crud = get_settlements_crud(supabase)
    settlement = await settlements_crud.get_settlement_by_id(settlement_id)
    
    if not settlement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Settlement not found"
        )
    
    return settlement


@router.get("/group/{group_id}", response_model=List[Settlements])
async def get_settlements_by_group(
    group_id: str,
    limit: int = Query(50, ge=1, le=100, 
                      description="Number of settlements to return"),
    offset: int = Query(0, ge=0, description="Number of settlements to skip"),
    supabase: Client = Depends(get_supabase)
):
    """
    Get all settlements for a group with pagination
    
    - **group_id**: ID of the group to get settlements for
    - **limit**: Maximum number of settlements to return (1-100)
    - **offset**: Number of settlements to skip for pagination
    """
    settlements_crud = get_settlements_crud(supabase)
    settlements = await settlements_crud.get_settlements_by_group(
        group_id, limit=limit, offset=offset)
    
    return settlements


@router.get("/user/{user_id}", response_model=List[Settlements])
async def get_settlements_by_user(
    user_id: str,
    limit: int = Query(50, ge=1, le=100, 
                      description="Number of settlements to return"),
    offset: int = Query(0, ge=0, description="Number of settlements to skip"),
    supabase: Client = Depends(get_supabase)
):
    """
    Get all settlements involving a user (either as payer or payee) with pagination
    
    - **user_id**: ID of the user to get settlements for
    - **limit**: Maximum number of settlements to return (1-100)
    - **offset**: Number of settlements to skip for pagination
    """
    settlements_crud = get_settlements_crud(supabase)
    settlements = await settlements_crud.get_settlements_by_user(
        user_id, limit=limit, offset=offset)
    
    return settlements


@router.get("/from/{from_user}", response_model=List[Settlements])
async def get_settlements_from_user(
    from_user: str,
    limit: int = Query(50, ge=1, le=100, 
                      description="Number of settlements to return"),
    offset: int = Query(0, ge=0, description="Number of settlements to skip"),
    supabase: Client = Depends(get_supabase)
):
    """
    Get all settlements where user is the payer with pagination
    
    - **from_user**: ID of the user who made the payments
    - **limit**: Maximum number of settlements to return (1-100)
    - **offset**: Number of settlements to skip for pagination
    """
    settlements_crud = get_settlements_crud(supabase)
    settlements = await settlements_crud.get_settlements_from_user(
        from_user, limit=limit, offset=offset)
    
    return settlements


@router.get("/to/{to_user}", response_model=List[Settlements])
async def get_settlements_to_user(
    to_user: str,
    limit: int = Query(50, ge=1, le=100, 
                      description="Number of settlements to return"),
    offset: int = Query(0, ge=0, description="Number of settlements to skip"),
    supabase: Client = Depends(get_supabase)
):
    """
    Get all settlements where user is the payee with pagination
    
    - **to_user**: ID of the user who received the payments
    - **limit**: Maximum number of settlements to return (1-100)
    - **offset**: Number of settlements to skip for pagination
    """
    settlements_crud = get_settlements_crud(supabase)
    settlements = await settlements_crud.get_settlements_to_user(
        to_user, limit=limit, offset=offset)
    
    return settlements


@router.get("/", response_model=List[Settlements])
async def get_pending_settlements(
    group_id: Optional[str] = Query(None, description="Filter by group ID"),
    limit: int = Query(50, ge=1, le=100, 
                      description="Number of settlements to return"),
    offset: int = Query(0, ge=0, description="Number of settlements to skip"),
    supabase: Client = Depends(get_supabase)
):
    """
    Get all pending settlements (not yet completed) with pagination
    
    - **group_id**: Optional group ID to filter by
    - **limit**: Maximum number of settlements to return (1-100)
    - **offset**: Number of settlements to skip for pagination
    """
    settlements_crud = get_settlements_crud(supabase)
    settlements = await settlements_crud.get_pending_settlements(
        group_id=group_id, limit=limit, offset=offset)
    
    return settlements


@router.get("/completed/", response_model=List[Settlements])
async def get_completed_settlements(
    group_id: Optional[str] = Query(None, description="Filter by group ID"),
    limit: int = Query(50, ge=1, le=100, 
                      description="Number of settlements to return"),
    offset: int = Query(0, ge=0, description="Number of settlements to skip"),
    supabase: Client = Depends(get_supabase)
):
    """
    Get all completed settlements (already settled) with pagination
    
    - **group_id**: Optional group ID to filter by
    - **limit**: Maximum number of settlements to return (1-100)
    - **offset**: Number of settlements to skip for pagination
    """
    settlements_crud = get_settlements_crud(supabase)
    settlements = await settlements_crud.get_completed_settlements(
        group_id=group_id, limit=limit, offset=offset)
    
    return settlements


@router.get("/between/{user1_id}/{user2_id}", response_model=List[Settlements])
async def get_settlements_between_users(
    user1_id: str,
    user2_id: str,
    group_id: Optional[str] = Query(None, description="Filter by group ID"),
    supabase: Client = Depends(get_supabase)
):
    """
    Get all settlements between two users
    
    - **user1_id**: ID of the first user
    - **user2_id**: ID of the second user
    - **group_id**: Optional group ID to filter by
    """
    settlements_crud = get_settlements_crud(supabase)
    settlements = await settlements_crud.get_settlements_between_users(
        user1_id, user2_id, group_id=group_id)
    
    return settlements


@router.put("/{settlement_id}", response_model=Settlements)
async def update_settlement(
    settlement_id: str,
    group_id: Optional[str] = None,
    from_user: Optional[str] = None,
    to_user: Optional[str] = None,
    amount: Optional[str] = None,
    method: Optional[str] = None,
    reference_id: Optional[str] = None,
    notes: Optional[str] = None,
    supabase: Client = Depends(get_supabase)
):
    """
    Update settlement information
    
    Only provided fields will be updated.
    """
    settlements_crud = get_settlements_crud(supabase)
    
    # Check if settlement exists
    existing_settlement = await settlements_crud.get_settlement_by_id(settlement_id)
    if not existing_settlement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Settlement not found"
        )
    
    # Validate that from_user and to_user are different if both are provided
    if from_user and to_user and from_user == to_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="From user and to user cannot be the same"
        )
    
    updated_settlement = await settlements_crud.update_settlement(
        settlement_id=settlement_id,
        group_id=group_id,
        from_user=from_user,
        to_user=to_user,
        amount=amount,
        method=method,
        reference_id=reference_id,
        notes=notes
    )
    
    if not updated_settlement:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update settlement"
        )
    
    return updated_settlement


@router.put("/{settlement_id}/complete", response_model=Settlements)
async def mark_settlement_completed(
    settlement_id: str,
    settled_at: Optional[datetime] = None,
    supabase: Client = Depends(get_supabase)
):
    """
    Mark a settlement as completed
    
    - **settlement_id**: ID of the settlement to complete
    - **settled_at**: Optional timestamp (defaults to current time)
    """
    settlements_crud = get_settlements_crud(supabase)
    
    # Check if settlement exists
    existing_settlement = await settlements_crud.get_settlement_by_id(settlement_id)
    if not existing_settlement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Settlement not found"
        )
    
    completed_settlement = await settlements_crud.mark_settlement_completed(
        settlement_id, settled_at=settled_at)
    
    if not completed_settlement:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark settlement as completed"
        )
    
    return completed_settlement


@router.put("/{settlement_id}/pending", response_model=Settlements)
async def mark_settlement_pending(
    settlement_id: str,
    supabase: Client = Depends(get_supabase)
):
    """
    Mark a settlement as pending (remove completion status)
    
    - **settlement_id**: ID of the settlement to mark as pending
    """
    settlements_crud = get_settlements_crud(supabase)
    
    # Check if settlement exists
    existing_settlement = await settlements_crud.get_settlement_by_id(settlement_id)
    if not existing_settlement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Settlement not found"
        )
    
    pending_settlement = await settlements_crud.mark_settlement_pending(settlement_id)
    
    if not pending_settlement:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark settlement as pending"
        )
    
    return pending_settlement


@router.delete("/{settlement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_settlement(
    settlement_id: str,
    supabase: Client = Depends(get_supabase)
):
    """Delete settlement"""
    settlements_crud = get_settlements_crud(supabase)
    
    # Check if settlement exists
    existing_settlement = await settlements_crud.get_settlement_by_id(settlement_id)
    if not existing_settlement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Settlement not found"
        )
    
    success = await settlements_crud.delete_settlement(settlement_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete settlement"
        )