from typing import List, Optional
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status, Query
from supabase import Client

from app.database import get_supabase
from app.crud.expenses import get_expenses_crud, ExpensesCRUD
from app.schemas.expenses import Expenses

router = APIRouter()


@router.post("/", response_model=Expenses, status_code=status.HTTP_201_CREATED)
async def create_expense(
    group_id: str,
    paid_by: str,
    amount: str,
    description: str,
    split_method: str,
    expense_date: date,
    category_id: Optional[str] = None,
    notes: Optional[str] = None,
    is_reimbursement: bool = False,
    supabase: Client = Depends(get_supabase),
):
    """
    Create a new expense
    
    - **group_id**: ID of the group this expense belongs to
    - **paid_by**: ID of the user who paid for this expense
    - **amount**: Amount of the expense
    - **description**: Description of the expense
    - **split_method**: How the expense should be split (equal, percentage, exact)
    - **expense_date**: Date when the expense occurred
    - **category_id**: Optional category ID for categorizing the expense
    - **notes**: Optional notes about the expense
    - **is_reimbursement**: Whether this expense is a reimbursement
    """
    expenses_crud = get_expenses_crud(supabase)
    
    expense = await expenses_crud.create_expense(
        group_id=group_id,
        paid_by=paid_by,
        amount=amount,
        description=description,
        split_method=split_method,
        expense_date=expense_date,
        category_id=category_id,
        notes=notes,
        is_reimbursement=is_reimbursement
    )
    
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create expense"
        )
    
    return expense


@router.get("/{expense_id}", response_model=Expenses)
async def get_expense(
    expense_id: str,
    supabase: Client = Depends(get_supabase),
):
    """Get expense by ID"""
    expenses_crud = get_expenses_crud(supabase)
    expense = await expenses_crud.get_expense_by_id(expense_id)
    
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    
    return expense


@router.get("/group/{group_id}", response_model=List[Expenses])
async def get_expenses_by_group(
    group_id: str,
    limit: int = Query(50, ge=1, le=100, 
                      description="Number of expenses to return"),
    offset: int = Query(0, ge=0, description="Number of expenses to skip"),
    supabase: Client = Depends(get_supabase)
):
    """
    Get all expenses for a group with pagination
    
    - **group_id**: ID of the group to get expenses for
    - **limit**: Maximum number of expenses to return (1-100)
    - **offset**: Number of expenses to skip for pagination
    """
    expenses_crud = get_expenses_crud(supabase)
    expenses = await expenses_crud.get_expenses_by_group(
        group_id, limit=limit, offset=offset)
    
    return expenses


@router.get("/user/{user_id}", response_model=List[Expenses])
async def get_expenses_by_user(
    user_id: str,
    limit: int = Query(50, ge=1, le=100, 
                      description="Number of expenses to return"),
    offset: int = Query(0, ge=0, description="Number of expenses to skip"),
    supabase: Client = Depends(get_supabase)
):
    """
    Get all expenses paid by a user with pagination
    
    - **user_id**: ID of the user to get expenses for
    - **limit**: Maximum number of expenses to return (1-100)
    - **offset**: Number of expenses to skip for pagination
    """
    expenses_crud = get_expenses_crud(supabase)
    expenses = await expenses_crud.get_expenses_by_user(
        user_id, limit=limit, offset=offset)
    
    return expenses


@router.get("/category/{category_id}", response_model=List[Expenses])
async def get_expenses_by_category(
    category_id: str,
    limit: int = Query(50, ge=1, le=100, 
                      description="Number of expenses to return"),
    offset: int = Query(0, ge=0, description="Number of expenses to skip"),
    supabase: Client = Depends(get_supabase)
):
    """
    Get all expenses for a specific category with pagination
    
    - **category_id**: ID of the category to get expenses for
    - **limit**: Maximum number of expenses to return (1-100)
    - **offset**: Number of expenses to skip for pagination
    """
    expenses_crud = get_expenses_crud(supabase)
    expenses = await expenses_crud.get_expenses_by_category(
        category_id, limit=limit, offset=offset)
    
    return expenses


@router.get("/group/{group_id}/date-range", response_model=List[Expenses])
async def get_expenses_by_date_range(
    group_id: str,
    start_date: date,
    end_date: date,
    supabase: Client = Depends(get_supabase)
):
    """
    Get expenses within a date range for a group
    
    - **group_id**: ID of the group to get expenses for
    - **start_date**: Start date for the range
    - **end_date**: End date for the range
    """
    expenses_crud = get_expenses_crud(supabase)
    expenses = await expenses_crud.get_expenses_by_date_range(
        group_id, start_date, end_date)
    
    return expenses


@router.put("/{expense_id}", response_model=Expenses)
async def update_expense(
    expense_id: str,
    group_id: Optional[str] = None,
    paid_by: Optional[str] = None,
    amount: Optional[str] = None,
    description: Optional[str] = None,
    category_id: Optional[str] = None,
    notes: Optional[str] = None,
    split_method: Optional[str] = None,
    expense_date: Optional[date] = None,
    is_reimbursement: Optional[bool] = None,
    supabase: Client = Depends(get_supabase)
):
    """
    Update expense information
    
    Only provided fields will be updated.
    """
    expenses_crud = get_expenses_crud(supabase)
    
    # Check if expense exists
    existing_expense = await expenses_crud.get_expense_by_id(expense_id)
    if not existing_expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    
    updated_expense = await expenses_crud.update_expense(
        expense_id=expense_id,
        group_id=group_id,
        paid_by=paid_by,
        amount=amount,
        description=description,
        category_id=category_id,
        notes=notes,
        split_method=split_method,
        expense_date=expense_date,
        is_reimbursement=is_reimbursement
    )
    
    if not updated_expense:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update expense"
        )
    
    return updated_expense


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    expense_id: str,
    supabase: Client = Depends(get_supabase)
):
    """Delete expense"""
    expenses_crud = get_expenses_crud(supabase)
    
    # Check if expense exists
    existing_expense = await expenses_crud.get_expense_by_id(expense_id)
    if not existing_expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    
    success = await expenses_crud.delete_expense(expense_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete expense"
        )
