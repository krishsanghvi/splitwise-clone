from pydantic import BaseModel, Field
import uuid
from datetime import date, datetime
from typing import Optional
from decimal import Decimal


class Balances(BaseModel):
    id: Optional[uuid.UUID] = None
    group_id: uuid.UUID
    user_from: uuid.UUID
    user_to: uuid.UUID
    amount: Decimal
    last_updated: Optional[datetime] = None
