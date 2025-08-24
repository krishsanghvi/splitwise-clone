from app.schemas.expenses import Expenses
from supabase import Client
from typing import Optional, List
import uuid
import logging
from datetime import date

logger = logging.getLogger(__name__)


class ExpensesCRUD:
    def __init__(self, supabase: Client):
        self.supabase = supabase

    async def create_expense(self, group_id: str, paid_by: str, amount: str, description: str, 
                           split_method: str, expense_date: date, category_id: str = None, 
                           notes: str = None, is_reimbursement: bool = False) -> Optional[Expenses]:
        """Create a new expense"""
        try:
            expense_data = {
                'group_id': group_id,
                'paid_by': paid_by,
                'amount': amount,
                'description': description,
                'split_method': split_method,
                'expense_date': expense_date.isoformat(),
                'is_reimbursement': is_reimbursement
            }
            
            if category_id:
                expense_data['category_id'] = category_id
            if notes:
                expense_data['notes'] = notes

            result = self.supabase.table('expenses').insert(expense_data).execute()

            if result.data:
                return Expenses(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error creating expense: {e}")
            return None

    async def get_expense_by_id(self, expense_id: str) -> Optional[Expenses]:
        """Get expense by ID"""
        try:
            result = self.supabase.table('expenses')\
                .select('*')\
                .eq('id', expense_id)\
                .execute()

            if result.data:
                return Expenses(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error getting expense by id {expense_id}: {e}")
            return None

    async def get_expenses_by_group(self, group_id: str, limit: int = 50, offset: int = 0) -> List[Expenses]:
        """Get all expenses for a group"""
        try:
            result = self.supabase.table('expenses')\
                .select('*')\
                .eq('group_id', group_id)\
                .order('expense_date', desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()

            return [Expenses(**expense) for expense in result.data]
        except Exception as e:
            logger.error(f"Error getting expenses for group {group_id}: {e}")
            return []

    async def get_expenses_by_user(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Expenses]:
        """Get all expenses paid by a user"""
        try:
            result = self.supabase.table('expenses')\
                .select('*')\
                .eq('paid_by', user_id)\
                .order('expense_date', desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()

            return [Expenses(**expense) for expense in result.data]
        except Exception as e:
            logger.error(f"Error getting expenses for user {user_id}: {e}")
            return []

    async def update_expense(self, expense_id: str, group_id: str = None, paid_by: str = None,
                           amount: str = None, description: str = None, category_id: str = None,
                           notes: str = None, split_method: str = None, expense_date: date = None,
                           is_reimbursement: bool = None) -> Optional[Expenses]:
        """Update expense information"""
        try:
            update_data = {}
            if group_id:
                update_data['group_id'] = group_id
            if paid_by:
                update_data['paid_by'] = paid_by
            if amount:
                update_data['amount'] = amount
            if description:
                update_data['description'] = description
            if category_id:
                update_data['category_id'] = category_id
            if notes is not None:  # Allow empty string
                update_data['notes'] = notes
            if split_method:
                update_data['split_method'] = split_method
            if expense_date:
                update_data['expense_date'] = expense_date.isoformat()
            if is_reimbursement is not None:
                update_data['is_reimbursement'] = is_reimbursement

            if not update_data:
                return await self.get_expense_by_id(expense_id)

            result = self.supabase.table('expenses')\
                .update(update_data)\
                .eq('id', expense_id)\
                .execute()

            if result.data:
                return Expenses(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error updating expense {expense_id}: {e}")
            return None

    async def delete_expense(self, expense_id: str) -> bool:
        """Delete expense"""
        try:
            result = self.supabase.table('expenses')\
                .delete()\
                .eq('id', expense_id)\
                .execute()

            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error deleting expense {expense_id}: {e}")
            return False

    async def get_expenses_by_category(self, category_id: str, limit: int = 50, offset: int = 0) -> List[Expenses]:
        """Get all expenses for a specific category"""
        try:
            result = self.supabase.table('expenses')\
                .select('*')\
                .eq('category_id', category_id)\
                .order('expense_date', desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()

            return [Expenses(**expense) for expense in result.data]
        except Exception as e:
            logger.error(f"Error getting expenses for category {category_id}: {e}")
            return []

    async def get_expenses_by_date_range(self, group_id: str, start_date: date, end_date: date) -> List[Expenses]:
        """Get expenses within a date range for a group"""
        try:
            result = self.supabase.table('expenses')\
                .select('*')\
                .eq('group_id', group_id)\
                .gte('expense_date', start_date.isoformat())\
                .lte('expense_date', end_date.isoformat())\
                .order('expense_date', desc=True)\
                .execute()

            return [Expenses(**expense) for expense in result.data]
        except Exception as e:
            logger.error(f"Error getting expenses by date range for group {group_id}: {e}")
            return []


def get_expenses_crud(supabase: Client) -> ExpensesCRUD:
    """Factory function to create ExpensesCRUD instance"""
    return ExpensesCRUD(supabase)