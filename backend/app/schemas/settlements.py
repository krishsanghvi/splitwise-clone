from operator import methodcaller
from pydantic import BaseModel, Field
import uuid
from typing import Optional
from decimal import Decimal
from datetime import datetime


class Settlements(BaseModel):
    id: Optional[uuid.UUID] = None
    group_id: uuid.UUID
    from_user: uuid.UUID
    to_user: uuid.UUID
    amount: Decimal
    method: str = "cash"
    reference_id: Optional[str] = None
    notes: Optional[str] = None
    settled_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
