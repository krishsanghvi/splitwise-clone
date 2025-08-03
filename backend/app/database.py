from supabase import Client, create_client
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class SupabaseConnection:
    def __init__(self):
        self.client: Client = None
        self.admin_client: Client = None

    def connect(self):
        try:
            self.client = create_client(
                settings.supabase_url, settings.supabase_key)
            self.admin_client = create_client(
                settings.supabase_url, settings.supabase_service_key)

            logger.info("Connected to Supabase successfully!")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            return False

    def get_client(self, admin: bool = False):
        if admin:
            return self.admin_client
        else:
            return self.client


# Global Instance
supabase_conn = SupabaseConnection()


def get_supabase(admin: bool = False):
    return supabase_conn.get_client(admin=admin)
