from app.schemas.groups import Groups
from supabase import Client
from typing import Optional, List
import uuid
import logging

logger = logging.getLogger(__name__)


class GroupCRUD:
    def __init__(self, supabase: Client):
        self.supabase = supabase

    async def create_group(self, created_by: str, name: str, description: str = None, invite_code: str = None) -> Optional[Groups]:
        """Create a new group"""
        try:
            result = self.supabase.table('groups').insert({
                'created_by': created_by,
                'group_name': name,
                'group_description': description,
                'invite_code': invite_code,
                'is_active': True
            }).execute()

            if result.data:
                return Groups(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error creating group: {e}")
            return None

    async def update_group(self, group_id: str, name: str = None, description: str = None, invite_code: str = None, is_active: bool = None) -> Optional[Groups]:
        """Update group information"""
        try:
            update_data = {}
            if name:
                update_data['group_name'] = name
            if description is not None:
                update_data['group_description'] = description
            if invite_code is not None:
                update_data['invite_code'] = invite_code
            if is_active is not None:
                update_data['is_active'] = is_active

            if not update_data:
                return await self.get_group_by_id(group_id)

            result = self.supabase.table('groups')\
                .update(update_data)\
                .eq('id', group_id)\
                .execute()

            if result.data:
                return Groups(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error updating group {group_id}: {e}")
            return None

    async def delete_group(self, group_id: str) -> bool:
        """Delete group (soft delete by setting is_active to False)"""
        try:
            result = self.supabase.table('groups')\
                .update({'is_active': False})\
                .eq('id', group_id)\
                .execute()

            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error deleting group {group_id}: {e}")
            return False

    async def get_group_by_id(self, group_id: str) -> Optional[Groups]:
        """Get group by ID"""
        try:
            result = self.supabase.table('groups')\
                .select('*')\
                .eq('id', group_id)\
                .eq('is_active', True)\
                .execute()

            if result.data:
                return Groups(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error getting group by id {group_id}: {e}")
            return None

    async def get_group_by_invite_code(self, invite_code: str) -> Optional[Groups]:
        """Get group by invite code"""
        try:
            result = self.supabase.table('groups')\
                .select('*')\
                .eq('invite_code', invite_code)\
                .eq('is_active', True)\
                .execute()

            if result.data:
                return Groups(**result.data[0])
            return None
        except Exception as e:
            logger.error(
                f"Error getting group by invite code {invite_code}: {e}")
            return None

    async def get_groups_by_user(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Groups]:
        """Get all groups created by a user"""
        try:
            result = self.supabase.table('groups')\
                .select('*')\
                .eq('created_by', user_id)\
                .eq('is_active', True)\
                .order('created_at', desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()

            return [Groups(**group) for group in result.data]
        except Exception as e:
            logger.error(f"Error getting groups for user {user_id}: {e}")
            return []

    async def search_groups(self, search_term: str, limit: int = 20) -> List[Groups]:
        """Search groups by name or description using Supabase RPC"""
        try:
            result = self.supabase.rpc(
                "search_groups", {"term": search_term, "max_limit": limit}
            ).execute()

            return [Groups(**group) for group in result.data or []]
        except Exception as e:
            logger.error(
                f"Error searching for groups with search term {search_term}: {e}")
            return []

    async def get_all_groups(self, limit: int = 50, offset: int = 0) -> List[Groups]:
        """Get all active groups with pagination"""
        try:
            result = self.supabase.table('groups')\
                .select('*')\
                .eq('is_active', True)\
                .order('created_at', desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()

            return [Groups(**group) for group in result.data]
        except Exception as e:
            logger.error(f"Error getting all groups: {e}")
            return []


def get_group_crud(supabase: Client) -> GroupCRUD:
    """Factory function to create GroupCRUD instance"""
    return GroupCRUD(supabase)
