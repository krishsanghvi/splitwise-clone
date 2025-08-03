from pydantic import BaseModel, Field
import uuid
from datetime import date, datetime
from typing import Optional
from decimal import Decimal


class ExpenseShares(BaseModel):
    id: Optional[uuid.UUID] = None
    expense_id: uuid.UUID
    user_id: uuid.UUID
    amount_owned: Decimal
    is_settled: bool
    created_at: Optional[datetime] = None
