from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime


class Transaction(BaseModel):
    id: int | None = None
    description: str = Field(min_length=1)
    amount: Decimal = Field(gt=0)
    category: str
    date: datetime = Field(default_factory=datetime.now)
    is_naffl_eligible: bool = True