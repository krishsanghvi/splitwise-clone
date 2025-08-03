from pydantic import BaseModel, Field
import uuid
from datetime import date, datetime
from typing import Optional


class Categories(BaseModel):
    id: Optional[uuid.UUID] = None
    name: str
    icon: str
    color: str
    is_default: bool
    created_at: Optional[datetime] = None
