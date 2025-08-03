from app.schemas.users import User
from supabase import Client
from typing import Optional, List
import uuid
import logging

logger = logging.getLogger(__name__)


class UserCRUD:
    def __init__(self, supabase: Client):
        self.supabase = supabase

    async def create_user(self, email: str, full_name: str, timezone: str = "UTC") -> Optional[User]:
        """Create a new user"""
        try:
            result = self.supabase.table('users').insert({
                'email': email,
                'full_name': full_name,
                'timezone': timezone
            }).execute()

            if result.data:
                return User(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None

    async def update_user(self, user_id: str, email: str = None, full_name: str = None, timezone: str = None) -> Optional[User]:
        """Update user information"""
        try:
            update_data = {}
            if email:
                update_data['email'] = email
            if full_name:
                update_data['full_name'] = full_name
            if timezone:
                update_data['timezone'] = timezone

            if not update_data:
                # No updates made
                return await self.get_user_by_id(user_id)

            result = self.supabase.table('users')\
                .update(update_data)\
                .eq('id', user_id)\
                .execute()

            if result.data:
                return User(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            return None

    async def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        try:
            result = self.supabase.table('users')\
                .delete()\
                .eq('id', user_id)\
                .execute()

            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            return False

    async def search_users(self, search_term: str, limit: int = 20) -> List[User]:
        """Search users by name or email"""
        try:
            result = self.supabase.table("users")\
                .select('*')\
                .or_(f'full_name.ilike.%{search_term}%,email.ilike.%{search_term}%')\
                .limit(limit)\
                .execute()

            return [User(**user) for user in result.data]

        except Exception as e:
            logger.error(
                f"Error searching for users with search term {search_term}: {e}")
            return []

    # async def list_users(self, limit: int = 50, offset: int = 0) -> List[User]:
    #     """List users with pagination"""
    #     try:
    #         result = self.supabase.table('users')\
    #             .select('*')\
    #             .order('created_at', desc=True)\
    #             .range(offset, offset + limit - 1)\
    #             .execute()

    #         return [User(**user) for user in result.data]
    #     except Exception as e:
    #         logger.error(f"Error listing users: {e}")
    #         return []

    async def get_user_by_id(self, id: str) -> Optional[User]:
        try:
            result = self.supabase.table('users')\
                .select('*')\
                .eq('id', id)\
                .execute()

            if result.data:
                return User(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error getting user by id {id}: {e}")
            return None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        try:
            result = self.supabase.table('users')\
                .select("*")\
                .eq("email", email)\
                .execute()

            if result.data:
                return User(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None

    async def get_all_users(self, limit: int = 50, offset: int = 0) -> List[User]:
        try:
            result = self.supabase.table('users')\
                .select('*')\
                .order('created_at', desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()

            return [User(**user) for user in result.data]
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []


def get_user_crud(supabase: Client) -> UserCRUD:
    """Factory function to create UserCRUD instance"""
    return UserCRUD(supabase)
