from pydantic import BaseModel, Field
import uuid
from datetime import date, datetime
from typing import Optional
from decimal import Decimal


class Expenses(BaseModel):
    id: Optional[uuid.UUID] = None
    group_id: uuid.UUID
    paid_by: uuid.UUID
    category_id: Optional[uuid.UUID] = None
    amount: Decimal
    description: str
    # receipt_url
    notes: Optional[str] = None
    split_method: str
    expense_date: date
    is_reimbursement: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
