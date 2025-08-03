from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from typing import Optional


class GroupMembers(BaseModel):
    id: Optional[uuid.UUID] = None
    group_id: uuid.UUID
    user_id: uuid.UUID
    role: str = "member"
    joined_at: Optional[datetime] = None
    is_active: bool = True
