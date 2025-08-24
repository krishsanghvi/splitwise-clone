from typing import Optional, List
import logging

from supabase import Client

from app.schemas.expense_shares import ExpenseShares

logger = logging.getLogger(__name__)


class ExpenseSharesCRUD:
    def __init__(self, supabase: Client):
        self.supabase = supabase

    async def create_expense_share(self, expense_id: str, user_id: str, 
                                 amount_owned: str, is_settled: bool = False) -> Optional[ExpenseShares]:
        """Create a new expense share"""
        try:
            expense_share_data = {
                'expense_id': expense_id,
                'user_id': user_id,
                'amount_owned': amount_owned,
                'is_settled': is_settled
            }

            result = self.supabase.table('expense_shares').insert(expense_share_data).execute()

            if result.data:
                return ExpenseShares(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error creating expense share: {e}")
            return None

    async def get_expense_share_by_id(self, share_id: str) -> Optional[ExpenseShares]:
        """Get expense share by ID"""
        try:
            result = self.supabase.table('expense_shares')\
                .select('*')\
                .eq('id', share_id)\
                .execute()

            if result.data:
                return ExpenseShares(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error getting expense share by id {share_id}: {e}")
            return None

    async def get_expense_shares_by_expense(self, expense_id: str) -> List[ExpenseShares]:
        """Get all expense shares for a specific expense"""
        try:
            result = self.supabase.table('expense_shares')\
                .select('*')\
                .eq('expense_id', expense_id)\
                .order('created_at', desc=False)\
                .execute()

            return [ExpenseShares(**share) for share in result.data]
        except Exception as e:
            logger.error(f"Error getting expense shares for expense {expense_id}: {e}")
            return []

    async def get_expense_shares_by_user(self, user_id: str, limit: int = 50, 
                                       offset: int = 0) -> List[ExpenseShares]:
        """Get all expense shares for a specific user"""
        try:
            result = self.supabase.table('expense_shares')\
                .select('*')\
                .eq('user_id', user_id)\
                .order('created_at', desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()

            return [ExpenseShares(**share) for share in result.data]
        except Exception as e:
            logger.error(f"Error getting expense shares for user {user_id}: {e}")
            return []

    async def get_unsettled_shares_by_user(self, user_id: str, limit: int = 50, 
                                         offset: int = 0) -> List[ExpenseShares]:
        """Get all unsettled expense shares for a specific user"""
        try:
            result = self.supabase.table('expense_shares')\
                .select('*')\
                .eq('user_id', user_id)\
                .eq('is_settled', False)\
                .order('created_at', desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()

            return [ExpenseShares(**share) for share in result.data]
        except Exception as e:
            logger.error(f"Error getting unsettled shares for user {user_id}: {e}")
            return []

    async def update_expense_share(self, share_id: str, expense_id: str = None,
                                 user_id: str = None, amount_owned: str = None,
                                 is_settled: bool = None) -> Optional[ExpenseShares]:
        """Update expense share information"""
        try:
            update_data = {}
            if expense_id:
                update_data['expense_id'] = expense_id
            if user_id:
                update_data['user_id'] = user_id
            if amount_owned:
                update_data['amount_owned'] = amount_owned
            if is_settled is not None:
                update_data['is_settled'] = is_settled

            if not update_data:
                return await self.get_expense_share_by_id(share_id)

            result = self.supabase.table('expense_shares')\
                .update(update_data)\
                .eq('id', share_id)\
                .execute()

            if result.data:
                return ExpenseShares(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error updating expense share {share_id}: {e}")
            return None

    async def delete_expense_share(self, share_id: str) -> bool:
        """Delete expense share"""
        try:
            result = self.supabase.table('expense_shares')\
                .delete()\
                .eq('id', share_id)\
                .execute()

            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error deleting expense share {share_id}: {e}")
            return False

    async def delete_expense_shares_by_expense(self, expense_id: str) -> bool:
        """Delete all expense shares for a specific expense"""
        try:
            result = self.supabase.table('expense_shares')\
                .delete()\
                .eq('expense_id', expense_id)\
                .execute()

            return True  # Always return True as deletion might not return data
        except Exception as e:
            logger.error(f"Error deleting expense shares for expense {expense_id}: {e}")
            return False

    async def settle_expense_share(self, share_id: str) -> Optional[ExpenseShares]:
        """Mark an expense share as settled"""
        return await self.update_expense_share(share_id, is_settled=True)

    async def unsettle_expense_share(self, share_id: str) -> Optional[ExpenseShares]:
        """Mark an expense share as unsettled"""
        return await self.update_expense_share(share_id, is_settled=False)


def get_expense_shares_crud(supabase: Client) -> ExpenseSharesCRUD:
    """Factory function to create ExpenseSharesCRUD instance"""
    return ExpenseSharesCRUD(supabase)