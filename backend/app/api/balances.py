from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from decimal import Decimal
from supabase import Client
from app.database import get_supabase
from app.crud.balances import get_balance_crud, BalanceCRUD
from app.schemas.balances import Balances

router = APIRouter()


@router.post("/", response_model=Balances, status_code=status.HTTP_201_CREATED)
async def create_or_update_balance(
    group_id: str,
    user_from: str,
    user_to: str,
    amount: Decimal,
    supabase: Client = Depends(get_supabase),
):
    """
    Create or update a balance between two users in a group

    - **group_id**: ID of the group
    - **user_from**: ID of the user who owes money
    - **user_to**: ID of the user who is owed money
    - **amount**: Amount owed (positive number)
    """
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be positive"
        )

    if user_from == user_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User cannot owe money to themselves"
        )

    balance_crud = get_balance_crud(supabase)
    balance = await balance_crud.create_or_update_balance(group_id, user_from, user_to, amount)
    
    if not balance:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create or update balance"
        )

    return balance


@router.get("/between", response_model=Balances)
async def get_balance_between_users(
    group_id: str,
    user_from: str,
    user_to: str,
    supabase: Client = Depends(get_supabase)
):
    """Get balance between two specific users in a group"""
    balance_crud = get_balance_crud(supabase)
    balance = await balance_crud.get_balance_between_users(group_id, user_from, user_to)

    if not balance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No balance found between these users"
        )

    return balance


@router.get("/{balance_id}", response_model=Balances)
async def get_balance(
    balance_id: str,
    supabase: Client = Depends(get_supabase),
):
    """Get balance by ID"""
    balance_crud = get_balance_crud(supabase)
    balance = await balance_crud.get_balance_by_id(balance_id)

    if not balance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Balance not found"
        )

    return balance


@router.get("/group/{group_id}/balances", response_model=List[Balances])
async def get_group_balances(
    group_id: str,
    limit: int = Query(50, ge=1, le=100, description="Number of balances to return"),
    offset: int = Query(0, ge=0, description="Number of balances to skip"),
    supabase: Client = Depends(get_supabase)
):
    """Get all balances for a specific group

    - **group_id**: ID of the group
    - **limit**: Maximum number of balances to return (1-100)
    - **offset**: Number of balances to skip for pagination
    """
    balance_crud = get_balance_crud(supabase)
    balances = await balance_crud.get_group_balances(group_id, limit=limit, offset=offset)

    return balances


@router.get("/group/{group_id}/user/{user_id}/balances", response_model=List[Balances])
async def get_user_balances_in_group(
    group_id: str,
    user_id: str,
    supabase: Client = Depends(get_supabase)
):
    """Get all balances involving a specific user in a group

    Returns both debts (where user owes others) and credits (where others owe user)
    """
    balance_crud = get_balance_crud(supabase)
    balances = await balance_crud.get_user_balances_in_group(group_id, user_id)

    return balances


@router.get("/group/{group_id}/user/{user_id}/total", response_model=dict)
async def get_user_total_balance(
    group_id: str,
    user_id: str,
    supabase: Client = Depends(get_supabase)
):
    """Get user's net balance in a group
    
    Returns:
    - Positive amount: Others owe this user money
    - Negative amount: This user owes others money
    - Zero: All settled
    """
    balance_crud = get_balance_crud(supabase)
    total_balance = await balance_crud.get_user_total_balance(group_id, user_id)

    return {
        "group_id": group_id,
        "user_id": user_id,
        "net_balance": total_balance,
        "status": "owed_money" if total_balance > 0 else "owes_money" if total_balance < 0 else "settled"
    }


@router.get("/group/{group_id}/summary", response_model=dict)
async def get_group_balance_summary(
    group_id: str,
    supabase: Client = Depends(get_supabase)
):
    """Get a comprehensive summary of all balances in a group
    
    Returns net balances for all users and raw balance data
    """
    balance_crud = get_balance_crud(supabase)
    summary = await balance_crud.get_group_balance_summary(group_id)

    return summary


@router.get("/user/{user_id}/balances", response_model=List[Balances])
async def get_all_user_balances(
    user_id: str,
    limit: int = Query(50, ge=1, le=100, description="Number of balances to return"),
    offset: int = Query(0, ge=0, description="Number of balances to skip"),
    supabase: Client = Depends(get_supabase)
):
    """Get all balances involving a user across all groups

    - **user_id**: ID of the user
    - **limit**: Maximum number of balances to return (1-100)
    - **offset**: Number of balances to skip for pagination
    """
    balance_crud = get_balance_crud(supabase)
    balances = await balance_crud.get_all_user_balances(user_id, limit=limit, offset=offset)

    return balances


@router.put("/{balance_id}/amount", response_model=Balances)
async def update_balance_amount(
    balance_id: str,
    amount: Decimal,
    supabase: Client = Depends(get_supabase)
):
    """Update the amount of a specific balance
    
    - **amount**: New amount (must be positive)
    """
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be positive"
        )

    balance_crud = get_balance_crud(supabase)
    
    # Check if balance exists
    existing_balance = await balance_crud.get_balance_by_id(balance_id)
    if not existing_balance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Balance not found"
        )

    updated_balance = await balance_crud.update_balance_amount(balance_id, amount)

    if not updated_balance:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update balance amount"
        )

    return updated_balance


@router.delete("/{balance_id}/settle", status_code=status.HTTP_204_NO_CONTENT)
async def settle_balance(
    balance_id: str,
    supabase: Client = Depends(get_supabase)
):
    """Settle a balance (mark as paid/delete the debt)
    
    This should be called when the debt has been paid and the balance should be cleared.
    """
    balance_crud = get_balance_crud(supabase)
    
    # Check if balance exists
    existing_balance = await balance_crud.get_balance_by_id(balance_id)
    if not existing_balance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Balance not found"
        )

    success = await balance_crud.settle_balance(balance_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to settle balance"
        )