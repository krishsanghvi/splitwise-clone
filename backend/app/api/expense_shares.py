from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from supabase import Client

from app.database import get_supabase
from app.crud.expense_shares import get_expense_shares_crud, ExpenseSharesCRUD
from app.schemas.expense_shares import ExpenseShares

router = APIRouter()


@router.post("/", response_model=ExpenseShares, status_code=status.HTTP_201_CREATED)
async def create_expense_share(
    expense_id: str,
    user_id: str,
    amount_owned: str,
    is_settled: bool = False,
    supabase: Client = Depends(get_supabase),
):
    """
    Create a new expense share
    
    - **expense_id**: ID of the expense this share belongs to
    - **user_id**: ID of the user who owes this share
    - **amount_owned**: Amount that the user owes
    - **is_settled**: Whether this share has been settled (defaults to False)
    """
    expense_shares_crud = get_expense_shares_crud(supabase)
    
    expense_share = await expense_shares_crud.create_expense_share(
        expense_id=expense_id,
        user_id=user_id,
        amount_owned=amount_owned,
        is_settled=is_settled
    )
    
    if not expense_share:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create expense share"
        )
    
    return expense_share


@router.get("/{share_id}", response_model=ExpenseShares)
async def get_expense_share(
    share_id: str,
    supabase: Client = Depends(get_supabase),
):
    """Get expense share by ID"""
    expense_shares_crud = get_expense_shares_crud(supabase)
    expense_share = await expense_shares_crud.get_expense_share_by_id(share_id)
    
    if not expense_share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense share not found"
        )
    
    return expense_share


@router.get("/expense/{expense_id}", response_model=List[ExpenseShares])
async def get_expense_shares_by_expense(
    expense_id: str,
    supabase: Client = Depends(get_supabase)
):
    """
    Get all expense shares for a specific expense
    
    - **expense_id**: ID of the expense to get shares for
    """
    expense_shares_crud = get_expense_shares_crud(supabase)
    expense_shares = await expense_shares_crud.get_expense_shares_by_expense(expense_id)
    
    return expense_shares


@router.get("/user/{user_id}", response_model=List[ExpenseShares])
async def get_expense_shares_by_user(
    user_id: str,
    limit: int = Query(50, ge=1, le=100, 
                      description="Number of expense shares to return"),
    offset: int = Query(0, ge=0, description="Number of expense shares to skip"),
    supabase: Client = Depends(get_supabase)
):
    """
    Get all expense shares for a specific user with pagination
    
    - **user_id**: ID of the user to get expense shares for
    - **limit**: Maximum number of expense shares to return (1-100)
    - **offset**: Number of expense shares to skip for pagination
    """
    expense_shares_crud = get_expense_shares_crud(supabase)
    expense_shares = await expense_shares_crud.get_expense_shares_by_user(
        user_id, limit=limit, offset=offset)
    
    return expense_shares


@router.get("/user/{user_id}/unsettled", response_model=List[ExpenseShares])
async def get_unsettled_shares_by_user(
    user_id: str,
    limit: int = Query(50, ge=1, le=100, 
                      description="Number of expense shares to return"),
    offset: int = Query(0, ge=0, description="Number of expense shares to skip"),
    supabase: Client = Depends(get_supabase)
):
    """
    Get all unsettled expense shares for a specific user with pagination
    
    - **user_id**: ID of the user to get unsettled expense shares for
    - **limit**: Maximum number of expense shares to return (1-100)
    - **offset**: Number of expense shares to skip for pagination
    """
    expense_shares_crud = get_expense_shares_crud(supabase)
    expense_shares = await expense_shares_crud.get_unsettled_shares_by_user(
        user_id, limit=limit, offset=offset)
    
    return expense_shares


@router.put("/{share_id}", response_model=ExpenseShares)
async def update_expense_share(
    share_id: str,
    expense_id: Optional[str] = None,
    user_id: Optional[str] = None,
    amount_owned: Optional[str] = None,
    is_settled: Optional[bool] = None,
    supabase: Client = Depends(get_supabase)
):
    """
    Update expense share information
    
    Only provided fields will be updated.
    """
    expense_shares_crud = get_expense_shares_crud(supabase)
    
    # Check if expense share exists
    existing_share = await expense_shares_crud.get_expense_share_by_id(share_id)
    if not existing_share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense share not found"
        )
    
    updated_share = await expense_shares_crud.update_expense_share(
        share_id=share_id,
        expense_id=expense_id,
        user_id=user_id,
        amount_owned=amount_owned,
        is_settled=is_settled
    )
    
    if not updated_share:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update expense share"
        )
    
    return updated_share


@router.put("/{share_id}/settle", response_model=ExpenseShares)
async def settle_expense_share(
    share_id: str,
    supabase: Client = Depends(get_supabase)
):
    """
    Mark an expense share as settled
    
    - **share_id**: ID of the expense share to settle
    """
    expense_shares_crud = get_expense_shares_crud(supabase)
    
    # Check if expense share exists
    existing_share = await expense_shares_crud.get_expense_share_by_id(share_id)
    if not existing_share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense share not found"
        )
    
    settled_share = await expense_shares_crud.settle_expense_share(share_id)
    
    if not settled_share:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to settle expense share"
        )
    
    return settled_share


@router.put("/{share_id}/unsettle", response_model=ExpenseShares)
async def unsettle_expense_share(
    share_id: str,
    supabase: Client = Depends(get_supabase)
):
    """
    Mark an expense share as unsettled
    
    - **share_id**: ID of the expense share to unsettle
    """
    expense_shares_crud = get_expense_shares_crud(supabase)
    
    # Check if expense share exists
    existing_share = await expense_shares_crud.get_expense_share_by_id(share_id)
    if not existing_share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense share not found"
        )
    
    unsettled_share = await expense_shares_crud.unsettle_expense_share(share_id)
    
    if not unsettled_share:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unsettle expense share"
        )
    
    return unsettled_share


@router.delete("/{share_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense_share(
    share_id: str,
    supabase: Client = Depends(get_supabase)
):
    """Delete expense share"""
    expense_shares_crud = get_expense_shares_crud(supabase)
    
    # Check if expense share exists
    existing_share = await expense_shares_crud.get_expense_share_by_id(share_id)
    if not existing_share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense share not found"
        )
    
    success = await expense_shares_crud.delete_expense_share(share_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete expense share"
        )


@router.delete("/expense/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense_shares_by_expense(
    expense_id: str,
    supabase: Client = Depends(get_supabase)
):
    """
    Delete all expense shares for a specific expense
    
    - **expense_id**: ID of the expense to delete shares for
    """
    expense_shares_crud = get_expense_shares_crud(supabase)
    
    success = await expense_shares_crud.delete_expense_shares_by_expense(expense_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete expense shares"
        )