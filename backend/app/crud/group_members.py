from app.schemas.group_members import GroupMembers
from supabase import Client
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

# member_id is id in the group_members table


class GroupMemberCRUD:
    def __init__(self, supabase: Client):
        self.supabase = supabase

    async def add_member(self, group_id: str, user_id: str, role: str = "member") -> Optional[GroupMembers]:
        """Add a new member to a group"""
        try:
            result = self.supabase.table('group_members').insert({
                'group_id': group_id,
                'user_id': user_id,
                'role': role,
                'is_active': True
            }).execute()

            if result.data:
                return GroupMembers(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error adding member to group: {e}")
            return None

    async def update_member_role(self, member_id: str, role: str) -> Optional[GroupMembers]:
        """Update member role in a group"""
        try:
            result = self.supabase.table('group_members')\
                .update({'role': role})\
                .eq('id', member_id)\
                .eq('is_active', True)\
                .execute()

            if result.data:
                return GroupMembers(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error updating member role {member_id}: {e}")
            return None

    async def remove_member(self, member_id: str) -> bool:
        """Remove member from group (soft delete)"""
        try:
            result = self.supabase.table('group_members')\
                .update({'is_active': False})\
                .eq('id', member_id)\
                .execute()

            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error removing member {member_id}: {e}")
            return False

    async def remove_member_by_user_and_group(self, group_id: str, user_id: str) -> bool:
        """Remove member from group by group_id and user_id"""
        try:
            result = self.supabase.table('group_members')\
                .update({'is_active': False})\
                .eq('group_id', group_id)\
                .eq('user_id', user_id)\
                .eq('is_active', True)\
                .execute()

            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error removing member from group {group_id}: {e}")
            return False

    async def get_member_by_id(self, member_id: str) -> Optional[GroupMembers]:
        """Get member by ID"""
        try:
            result = self.supabase.table('group_members')\
                .select('*')\
                .eq('id', member_id)\
                .eq('is_active', True)\
                .execute()

            if result.data:
                return GroupMembers(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error getting member by id {member_id}: {e}")
            return None

    async def get_member_by_user_and_group(self, group_id: str, user_id: str) -> Optional[GroupMembers]:
        """Get member by group_id and user_id"""
        try:
            result = self.supabase.table('group_members')\
                .select('*')\
                .eq('group_id', group_id)\
                .eq('user_id', user_id)\
                .eq('is_active', True)\
                .execute()

            if result.data:
                return GroupMembers(**result.data[0])
            return None
        except Exception as e:
            logger.error(
                f"Error getting member for group {group_id} and user {user_id}: {e}")
            return None

    async def get_group_members(self, group_id: str, limit: int = 50, offset: int = 0) -> List[GroupMembers]:
        """Get all active members of a group"""
        try:
            result = self.supabase.table('group_members')\
                .select('*')\
                .eq('group_id', group_id)\
                .eq('is_active', True)\
                .order('joined_at', desc=False)\
                .range(offset, offset + limit - 1)\
                .execute()

            return [GroupMembers(**member) for member in result.data]
        except Exception as e:
            logger.error(f"Error getting members for group {group_id}: {e}")
            return []

    async def get_user_groups(self, user_id: str, limit: int = 50, offset: int = 0) -> List[GroupMembers]:
        """Get all groups a user is a member of"""
        try:
            result = self.supabase.table('group_members')\
                .select('*')\
                .eq('user_id', user_id)\
                .eq('is_active', True)\
                .order('joined_at', desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()

            return [GroupMembers(**member) for member in result.data]
        except Exception as e:
            logger.error(f"Error getting groups for user {user_id}: {e}")
            return []

    async def is_member(self, group_id: str, user_id: str) -> bool:
        """Check if user is an active member of a group"""
        try:
            result = self.supabase.table('group_members')\
                .select('id')\
                .eq('group_id', group_id)\
                .eq('user_id', user_id)\
                .eq('is_active', True)\
                .execute()

            return len(result.data) > 0
        except Exception as e:
            logger.error(
                f"Error checking membership for group {group_id} and user {user_id}: {e}")
            return False

    async def is_admin(self, group_id: str, user_id: str) -> bool:
        """Check if user is an admin/owner of a group"""
        try:
            result = self.supabase.table('group_members')\
                .select('role')\
                .eq('group_id', group_id)\
                .eq('user_id', user_id)\
                .eq('is_active', True)\
                .execute()

            if result.data:
                return result.data[0]['role'] in ['admin']
            return False
        except Exception as e:
            logger.error(
                f"Error checking admin status for group {group_id} and user {user_id}: {e}")
            return False

    async def get_group_admins(self, group_id: str) -> List[GroupMembers]:
        """Get all admins/owners of a group"""
        try:
            result = self.supabase.table('group_members')\
                .select('*')\
                .eq('group_id', group_id)\
                .in_('role', ['admin'])\
                .eq('is_active', True)\
                .execute()

            return [GroupMembers(**member) for member in result.data]
        except Exception as e:
            logger.error(f"Error getting admins for group {group_id}: {e}")
            return []


def get_group_member_crud(supabase: Client) -> GroupMemberCRUD:
    """Factory function to create GroupMemberCRUD instance"""
    return GroupMemberCRUD(supabase)
