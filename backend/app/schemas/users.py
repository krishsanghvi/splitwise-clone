from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from typing import Optional


class User(BaseModel):
    id: Optional[uuid.UUID] = None
    email: str
    full_name: str
    timezone: str = "UTC"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
