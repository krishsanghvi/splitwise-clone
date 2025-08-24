from typing import Optional, List
import logging
from datetime import datetime

from supabase import Client

from app.schemas.settlements import Settlements

logger = logging.getLogger(__name__)


class SettlementsCRUD:
    def __init__(self, supabase: Client):
        self.supabase = supabase

    async def create_settlement(self, group_id: str, from_user: str, to_user: str,
                              amount: str, method: str = "cash", reference_id: str = None,
                              notes: str = None) -> Optional[Settlements]:
        """Create a new settlement"""
        try:
            settlement_data = {
                'group_id': group_id,
                'from_user': from_user,
                'to_user': to_user,
                'amount': amount,
                'method': method
            }
            
            if reference_id:
                settlement_data['reference_id'] = reference_id
            if notes:
                settlement_data['notes'] = notes

            result = self.supabase.table('settlements').insert(settlement_data).execute()

            if result.data:
                return Settlements(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error creating settlement: {e}")
            return None

    async def get_settlement_by_id(self, settlement_id: str) -> Optional[Settlements]:
        """Get settlement by ID"""
        try:
            result = self.supabase.table('settlements')\
                .select('*')\
                .eq('id', settlement_id)\
                .execute()

            if result.data:
                return Settlements(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error getting settlement by id {settlement_id}: {e}")
            return None

    async def get_settlements_by_group(self, group_id: str, limit: int = 50, 
                                     offset: int = 0) -> List[Settlements]:
        """Get all settlements for a group"""
        try:
            result = self.supabase.table('settlements')\
                .select('*')\
                .eq('group_id', group_id)\
                .order('created_at', desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()

            return [Settlements(**settlement) for settlement in result.data]
        except Exception as e:
            logger.error(f"Error getting settlements for group {group_id}: {e}")
            return []

    async def get_settlements_by_user(self, user_id: str, limit: int = 50, 
                                    offset: int = 0) -> List[Settlements]:
        """Get all settlements involving a user (either as payer or payee)"""
        try:
            result = self.supabase.table('settlements')\
                .select('*')\
                .or_(f'from_user.eq.{user_id},to_user.eq.{user_id}')\
                .order('created_at', desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()

            return [Settlements(**settlement) for settlement in result.data]
        except Exception as e:
            logger.error(f"Error getting settlements for user {user_id}: {e}")
            return []

    async def get_settlements_from_user(self, from_user: str, limit: int = 50, 
                                      offset: int = 0) -> List[Settlements]:
        """Get all settlements where user is the payer"""
        try:
            result = self.supabase.table('settlements')\
                .select('*')\
                .eq('from_user', from_user)\
                .order('created_at', desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()

            return [Settlements(**settlement) for settlement in result.data]
        except Exception as e:
            logger.error(f"Error getting settlements from user {from_user}: {e}")
            return []

    async def get_settlements_to_user(self, to_user: str, limit: int = 50, 
                                    offset: int = 0) -> List[Settlements]:
        """Get all settlements where user is the payee"""
        try:
            result = self.supabase.table('settlements')\
                .select('*')\
                .eq('to_user', to_user)\
                .order('created_at', desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()

            return [Settlements(**settlement) for settlement in result.data]
        except Exception as e:
            logger.error(f"Error getting settlements to user {to_user}: {e}")
            return []

    async def get_pending_settlements(self, group_id: str = None, limit: int = 50, 
                                    offset: int = 0) -> List[Settlements]:
        """Get all pending settlements (not yet settled)"""
        try:
            query = self.supabase.table('settlements')\
                .select('*')\
                .is_('settled_at', 'null')

            if group_id:
                query = query.eq('group_id', group_id)

            result = query.order('created_at', desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()

            return [Settlements(**settlement) for settlement in result.data]
        except Exception as e:
            logger.error(f"Error getting pending settlements: {e}")
            return []

    async def get_completed_settlements(self, group_id: str = None, limit: int = 50, 
                                      offset: int = 0) -> List[Settlements]:
        """Get all completed settlements (already settled)"""
        try:
            query = self.supabase.table('settlements')\
                .select('*')\
                .not_.is_('settled_at', 'null')

            if group_id:
                query = query.eq('group_id', group_id)

            result = query.order('settled_at', desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()

            return [Settlements(**settlement) for settlement in result.data]
        except Exception as e:
            logger.error(f"Error getting completed settlements: {e}")
            return []

    async def update_settlement(self, settlement_id: str, group_id: str = None,
                              from_user: str = None, to_user: str = None,
                              amount: str = None, method: str = None,
                              reference_id: str = None, notes: str = None,
                              settled_at: datetime = None) -> Optional[Settlements]:
        """Update settlement information"""
        try:
            update_data = {}
            if group_id:
                update_data['group_id'] = group_id
            if from_user:
                update_data['from_user'] = from_user
            if to_user:
                update_data['to_user'] = to_user
            if amount:
                update_data['amount'] = amount
            if method:
                update_data['method'] = method
            if reference_id is not None:  # Allow empty string
                update_data['reference_id'] = reference_id
            if notes is not None:  # Allow empty string
                update_data['notes'] = notes
            if settled_at is not None:
                update_data['settled_at'] = settled_at.isoformat()

            if not update_data:
                return await self.get_settlement_by_id(settlement_id)

            result = self.supabase.table('settlements')\
                .update(update_data)\
                .eq('id', settlement_id)\
                .execute()

            if result.data:
                return Settlements(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error updating settlement {settlement_id}: {e}")
            return None

    async def mark_settlement_completed(self, settlement_id: str, 
                                      settled_at: datetime = None) -> Optional[Settlements]:
        """Mark a settlement as completed"""
        if settled_at is None:
            settled_at = datetime.now()
        
        return await self.update_settlement(settlement_id, settled_at=settled_at)

    async def mark_settlement_pending(self, settlement_id: str) -> Optional[Settlements]:
        """Mark a settlement as pending (remove settled_at timestamp)"""
        try:
            result = self.supabase.table('settlements')\
                .update({'settled_at': None})\
                .eq('id', settlement_id)\
                .execute()

            if result.data:
                return Settlements(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error marking settlement {settlement_id} as pending: {e}")
            return None

    async def delete_settlement(self, settlement_id: str) -> bool:
        """Delete settlement"""
        try:
            result = self.supabase.table('settlements')\
                .delete()\
                .eq('id', settlement_id)\
                .execute()

            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error deleting settlement {settlement_id}: {e}")
            return False

    async def get_settlements_between_users(self, user1_id: str, user2_id: str,
                                          group_id: str = None) -> List[Settlements]:
        """Get all settlements between two users"""
        try:
            query = self.supabase.table('settlements')\
                .select('*')\
                .or_(f'and(from_user.eq.{user1_id},to_user.eq.{user2_id}),'
                     f'and(from_user.eq.{user2_id},to_user.eq.{user1_id})')

            if group_id:
                query = query.eq('group_id', group_id)

            result = query.order('created_at', desc=True).execute()

            return [Settlements(**settlement) for settlement in result.data]
        except Exception as e:
            logger.error(f"Error getting settlements between users {user1_id} and {user2_id}: {e}")
            return []


def get_settlements_crud(supabase: Client) -> SettlementsCRUD:
    """Factory function to create SettlementsCRUD instance"""
    return SettlementsCRUD(supabase)