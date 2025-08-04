from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from supabase import Client
from app.database import get_supabase
from app.crud.categories import get_category_crud, CategoryCRUD
from app.schemas.categories import Categories

router = APIRouter()


@router.post("/", response_model=Categories, status_code=status.HTTP_201_CREATED)
async def create_category(
    name: str,
    icon: str,
    color: str,
    is_default: bool = False,
    supabase: Client = Depends(get_supabase),
):
    """
    Create a new category

    - **name**: Category name (must be unique)
    - **icon**: Icon identifier for the category
    - **color**: Color code for the category (e.g., #FF5733)
    - **is_default**: Whether this is a default system category
    """
    category_crud = get_category_crud(supabase)

    # Check if category name already exists
    existing_category = await category_crud.get_category_by_name(name)
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )

    category = await category_crud.create_category(name, icon, color, is_default)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create category"
        )

    return category


@router.get("/search", response_model=List[Categories])
async def search_categories(
    search_term: str,
    limit: int = Query(20, ge=1, le=100, description="Number of categories to return"),
    supabase: Client = Depends(get_supabase)
):
    """Search categories by name"""
    category_crud = get_category_crud(supabase)
    categories = await category_crud.search_categories(search_term, limit)
    return categories


@router.get("/{category_id}", response_model=Categories)
async def get_category(
    category_id: str,
    supabase: Client = Depends(get_supabase),
):
    """Get category by ID"""
    category_crud = get_category_crud(supabase)
    category = await category_crud.get_category_by_id(category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    return category


@router.get("/name/{name}", response_model=Categories)
async def get_category_by_name(
    name: str,
    supabase: Client = Depends(get_supabase)
):
    """Get category by name"""
    category_crud = get_category_crud(supabase)
    category = await category_crud.get_category_by_name(name)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category


@router.get("/", response_model=List[Categories])
async def get_all_categories(
    limit: int = Query(50, ge=1, le=100, description="Number of categories to return"),
    offset: int = Query(0, ge=0, description="Number of categories to skip"),
    supabase: Client = Depends(get_supabase)
):
    """List all categories with pagination

    - **limit**: Maximum number of categories to return (1-100)
    - **offset**: Number of categories to skip for pagination
    """
    category_crud = get_category_crud(supabase)
    categories = await category_crud.get_all_categories(limit=limit, offset=offset)

    return categories


@router.get("/default/list", response_model=List[Categories])
async def get_default_categories(
    supabase: Client = Depends(get_supabase)
):
    """Get all default system categories"""
    category_crud = get_category_crud(supabase)
    categories = await category_crud.get_default_categories()

    return categories


@router.get("/custom/list", response_model=List[Categories])
async def get_custom_categories(
    supabase: Client = Depends(get_supabase)
):
    """Get all custom (non-default) categories"""
    category_crud = get_category_crud(supabase)
    categories = await category_crud.get_custom_categories()

    return categories


@router.put("/{category_id}", response_model=Categories)
async def update_category(
    category_id: str,
    name: Optional[str] = None,
    icon: Optional[str] = None,
    color: Optional[str] = None,
    is_default: Optional[bool] = None,
    supabase: Client = Depends(get_supabase)
):
    """Update category information
    - **name**: New category name (optional)
    - **icon**: New icon identifier (optional)  
    - **color**: New color code (optional)
    - **is_default**: New default status (optional)

    Only provided fields will be updated.
    """
    category_crud = get_category_crud(supabase)

    # Check if category exists
    existing_category = await category_crud.get_category_by_id(category_id)
    if not existing_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    # Check if new name is already in use by another category
    if name and name != existing_category.name:
        existing_category_with_name = await category_crud.get_category_by_name(name)
        if existing_category_with_name and str(existing_category_with_name.id) != category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name already in use"
            )

    updated_category = await category_crud.update_category(category_id, name, icon, color, is_default)

    if not updated_category:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update category"
        )

    return updated_category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: str,
    supabase: Client = Depends(get_supabase)
):
    """Delete category
    
    Note: Be careful when deleting categories as this may affect existing expenses.
    Consider soft delete or archiving for categories with associated expenses.
    """
    category_crud = get_category_crud(supabase)
    existing_category = await category_crud.get_category_by_id(category_id)
    if not existing_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    # Prevent deletion of default categories (optional business rule)
    if existing_category.is_default:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete default system categories"
        )

    success = await category_crud.delete_category(category_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete category"
        )