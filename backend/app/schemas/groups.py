from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from typing import Optional


class Groups(BaseModel):
    id: Optional[uuid.UUID] = None
    created_by: Optional[uuid.UUID] = None
    name: str
    description: Optional[str] = None
    invite_code: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
