from app.schemas.categories import Categories
from supabase import Client
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class CategoryCRUD:
    def __init__(self, supabase: Client):
        self.supabase = supabase

    async def create_category(self, name: str, icon: str, color: str, is_default: bool = False) -> Optional[Categories]:
        """Create a new category"""
        try:
            result = self.supabase.table('categories').insert({
                'name': name,
                'icon': icon,
                'color': color,
                'is_default': is_default
            }).execute()

            if result.data:
                return Categories(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error creating category: {e}")
            return None

    async def update_category(self, category_id: str, name: str = None, icon: str = None, color: str = None, is_default: bool = None) -> Optional[Categories]:
        """Update category information"""
        try:
            update_data = {}
            if name is not None:
                update_data['name'] = name
            if icon is not None:
                update_data['icon'] = icon
            if color is not None:
                update_data['color'] = color
            if is_default is not None:
                update_data['is_default'] = is_default

            if not update_data:
                return await self.get_category_by_id(category_id)

            result = self.supabase.table('categories')\
                .update(update_data)\
                .eq('id', category_id)\
                .execute()

            if result.data:
                return Categories(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error updating category {category_id}: {e}")
            return None

    async def delete_category(self, category_id: str) -> bool:
        """Delete category (hard delete since categories are system-level)"""
        try:
            result = self.supabase.table('categories')\
                .delete()\
                .eq('id', category_id)\
                .execute()

            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error deleting category {category_id}: {e}")
            return False

    async def get_category_by_id(self, category_id: str) -> Optional[Categories]:
        """Get category by ID"""
        try:
            result = self.supabase.table('categories')\
                .select('*')\
                .eq('id', category_id)\
                .execute()

            if result.data:
                return Categories(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error getting category by id {category_id}: {e}")
            return None

    async def get_category_by_name(self, name: str) -> Optional[Categories]:
        """Get category by name"""
        try:
            result = self.supabase.table('categories')\
                .select('*')\
                .eq('name', name)\
                .execute()

            if result.data:
                return Categories(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error getting category by name {name}: {e}")
            return None

    async def get_all_categories(self, limit: int = 50, offset: int = 0) -> List[Categories]:
        """Get all categories with pagination"""
        try:
            result = self.supabase.table('categories')\
                .select('*')\
                .order('name', desc=False)\
                .range(offset, offset + limit - 1)\
                .execute()

            return [Categories(**category) for category in result.data]
        except Exception as e:
            logger.error(f"Error getting all categories: {e}")
            return []

    async def get_default_categories(self) -> List[Categories]:
        """Get all default categories"""
        try:
            result = self.supabase.table('categories')\
                .select('*')\
                .eq('is_default', True)\
                .order('name', desc=False)\
                .execute()

            return [Categories(**category) for category in result.data]
        except Exception as e:
            logger.error(f"Error getting default categories: {e}")
            return []

    async def get_custom_categories(self) -> List[Categories]:
        """Get all custom (non-default) categories"""
        try:
            result = self.supabase.table('categories')\
                .select('*')\
                .eq('is_default', False)\
                .order('name', desc=False)\
                .execute()

            return [Categories(**category) for category in result.data]
        except Exception as e:
            logger.error(f"Error getting custom categories: {e}")
            return []

    async def search_categories(self, search_term: str, limit: int = 20) -> List[Categories]:
        """Search categories by name"""
        try:
            result = self.supabase.table('categories')\
                .select('*')\
                .ilike('name', f'%{search_term}%')\
                .order('name', desc=False)\
                .limit(limit)\
                .execute()

            return [Categories(**category) for category in result.data]
        except Exception as e:
            logger.error(f"Error searching categories with term {search_term}: {e}")
            return []


def get_category_crud(supabase: Client) -> CategoryCRUD:
    """Factory function to create CategoryCRUD instance"""
    return CategoryCRUD(supabase)