from sqlmodel import SQLModel, Field
from datetime import datetime, date as Date
from decimal import Decimal
from typing import Optional


# Persistent models (stored in database)
class Expense(SQLModel, table=True):
    __tablename__ = "expenses"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    description: str = Field(max_length=500)
    amount: Decimal = Field(decimal_places=2)
    date: Date = Field()
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Non-persistent schemas (for validation, forms, API requests/responses)
class ExpenseCreate(SQLModel, table=False):
    description: str = Field(max_length=500)
    amount: Decimal = Field(decimal_places=2)
    date: Date


class ExpenseUpdate(SQLModel, table=False):
    description: Optional[str] = Field(default=None, max_length=500)
    amount: Optional[Decimal] = Field(default=None, decimal_places=2)
    date: Optional[Date] = Field(default=None)
