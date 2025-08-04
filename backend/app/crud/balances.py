from app.schemas.balances import Balances
from supabase import Client
from typing import Optional, List
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class BalanceCRUD:
    def __init__(self, supabase: Client):
        self.supabase = supabase

    async def create_or_update_balance(self, group_id: str, user_from: str, user_to: str, amount: Decimal) -> Optional[Balances]:
        """Create a new balance or update existing balance between two users"""
        try:
            # First check if balance already exists
            existing_balance = await self.get_balance_between_users(group_id, user_from, user_to)
            
            if existing_balance:
                # Update existing balance
                new_amount = existing_balance.amount + amount
                result = self.supabase.table('balances')\
                    .update({'amount': str(new_amount)})\
                    .eq('id', str(existing_balance.id))\
                    .execute()
            else:
                # Create new balance
                result = self.supabase.table('balances').insert({
                    'group_id': group_id,
                    'user_from': user_from,
                    'user_to': user_to,
                    'amount': str(amount)
                }).execute()

            if result.data:
                return Balances(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error creating/updating balance: {e}")
            return None

    async def get_balance_by_id(self, balance_id: str) -> Optional[Balances]:
        """Get balance by ID"""
        try:
            result = self.supabase.table('balances')\
                .select('*')\
                .eq('id', balance_id)\
                .execute()

            if result.data:
                return Balances(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error getting balance by id {balance_id}: {e}")
            return None

    async def get_balance_between_users(self, group_id: str, user_from: str, user_to: str) -> Optional[Balances]:
        """Get balance between two specific users in a group"""
        try:
            result = self.supabase.table('balances')\
                .select('*')\
                .eq('group_id', group_id)\
                .eq('user_from', user_from)\
                .eq('user_to', user_to)\
                .execute()

            if result.data:
                return Balances(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error getting balance between users {user_from} and {user_to}: {e}")
            return None

    async def get_group_balances(self, group_id: str, limit: int = 50, offset: int = 0) -> List[Balances]:
        """Get all balances for a specific group"""
        try:
            result = self.supabase.table('balances')\
                .select('*')\
                .eq('group_id', group_id)\
                .order('last_updated', desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()

            return [Balances(**balance) for balance in result.data]
        except Exception as e:
            logger.error(f"Error getting balances for group {group_id}: {e}")
            return []

    async def get_user_balances_in_group(self, group_id: str, user_id: str) -> List[Balances]:
        """Get all balances involving a specific user in a group (both as creditor and debtor)"""
        try:
            # Get balances where user owes others
            owes_result = self.supabase.table('balances')\
                .select('*')\
                .eq('group_id', group_id)\
                .eq('user_from', user_id)\
                .execute()

            # Get balances where others owe user
            owed_result = self.supabase.table('balances')\
                .select('*')\
                .eq('group_id', group_id)\
                .eq('user_to', user_id)\
                .execute()

            balances = []
            if owes_result.data:
                balances.extend([Balances(**balance) for balance in owes_result.data])
            if owed_result.data:
                balances.extend([Balances(**balance) for balance in owed_result.data])

            return balances
        except Exception as e:
            logger.error(f"Error getting user balances for user {user_id} in group {group_id}: {e}")
            return []

    async def get_user_total_balance(self, group_id: str, user_id: str) -> Decimal:
        """Calculate user's net balance in a group (positive means others owe them, negative means they owe others)"""
        try:
            balances = await self.get_user_balances_in_group(group_id, user_id)
            total = Decimal('0')
            
            for balance in balances:
                if str(balance.user_to) == user_id:
                    # Others owe this user
                    total += balance.amount
                elif str(balance.user_from) == user_id:
                    # This user owes others
                    total -= balance.amount
            
            return total
        except Exception as e:
            logger.error(f"Error calculating total balance for user {user_id} in group {group_id}: {e}")
            return Decimal('0')

    async def settle_balance(self, balance_id: str) -> bool:
        """Settle/delete a balance (when debt is paid)"""
        try:
            result = self.supabase.table('balances')\
                .delete()\
                .eq('id', balance_id)\
                .execute()

            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error settling balance {balance_id}: {e}")
            return False

    async def update_balance_amount(self, balance_id: str, new_amount: Decimal) -> Optional[Balances]:
        """Update the amount of a specific balance"""
        try:
            result = self.supabase.table('balances')\
                .update({'amount': str(new_amount)})\
                .eq('id', balance_id)\
                .execute()

            if result.data:
                return Balances(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error updating balance amount {balance_id}: {e}")
            return None

    async def get_group_balance_summary(self, group_id: str) -> dict:
        """Get a summary of all balances in a group with net amounts"""
        try:
            balances = await self.get_group_balances(group_id)
            
            # Calculate net balances for each user
            user_net_balances = {}
            
            for balance in balances:
                user_from = str(balance.user_from)
                user_to = str(balance.user_to)
                amount = balance.amount
                
                # Initialize users if not in dict
                if user_from not in user_net_balances:
                    user_net_balances[user_from] = Decimal('0')
                if user_to not in user_net_balances:
                    user_net_balances[user_to] = Decimal('0')
                
                # user_from owes user_to
                user_net_balances[user_from] -= amount
                user_net_balances[user_to] += amount
            
            return {
                'group_id': group_id,
                'total_balances': len(balances),
                'user_net_balances': user_net_balances,
                'raw_balances': balances
            }
        except Exception as e:
            logger.error(f"Error getting balance summary for group {group_id}: {e}")
            return {'group_id': group_id, 'error': str(e)}

    async def get_all_user_balances(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Balances]:
        """Get all balances involving a user across all groups"""
        try:
            # Get balances where user owes others
            owes_result = self.supabase.table('balances')\
                .select('*')\
                .eq('user_from', user_id)\
                .order('last_updated', desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()

            # Get balances where others owe user
            owed_result = self.supabase.table('balances')\
                .select('*')\
                .eq('user_to', user_id)\
                .order('last_updated', desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()

            balances = []
            if owes_result.data:
                balances.extend([Balances(**balance) for balance in owes_result.data])
            if owed_result.data:
                balances.extend([Balances(**balance) for balance in owed_result.data])

            # Sort by last_updated desc
            balances.sort(key=lambda x: x.last_updated or x.id, reverse=True)
            
            return balances[:limit]  # Apply limit after combining
        except Exception as e:
            logger.error(f"Error getting all balances for user {user_id}: {e}")
            return []


def get_balance_crud(supabase: Client) -> BalanceCRUD:
    """Factory function to create BalanceCRUD instance"""
    return BalanceCRUD(supabase)