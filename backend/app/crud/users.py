from schemas.users import User
from supabase import Client
from typing import Optional
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

    async def list_users(self, limit: int = 50, offset: int = 0) -> List[User]:
        """List users with pagination"""
        try:
            result = self.supabase.table('users')\
                .select('*')\
                .order('created_at', desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()

            return [User(**user) for user in result.data]
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return []


def get_user_crud(supabase: Client) -> UserCRUD:
    """Factory function to create UserCRUD instance"""
    return UserCRUD(supabase)
