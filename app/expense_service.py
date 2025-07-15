from decimal import Decimal
from typing import List, Optional
from sqlmodel import select, desc
from app.database import get_session
from app.models import Expense, ExpenseCreate


def create_expense(expense_data: ExpenseCreate) -> Expense:
    """Create a new expense in the database."""
    with get_session() as session:
        expense = Expense(description=expense_data.description, amount=expense_data.amount, date=expense_data.date)
        session.add(expense)
        session.commit()
        session.refresh(expense)
        return expense


def get_all_expenses() -> List[Expense]:
    """Retrieve all expenses from the database, ordered by date (newest first)."""
    with get_session() as session:
        statement = select(Expense).order_by(desc(Expense.date))
        expenses = session.exec(statement).all()
        return list(expenses)


def get_expense_by_id(expense_id: int) -> Optional[Expense]:
    """Retrieve a specific expense by ID."""
    with get_session() as session:
        expense = session.get(Expense, expense_id)
        return expense


def delete_expense(expense_id: int) -> bool:
    """Delete an expense by ID. Returns True if successful, False if not found."""
    with get_session() as session:
        expense = session.get(Expense, expense_id)
        if expense is None:
            return False
        session.delete(expense)
        session.commit()
        return True


def get_total_expenses() -> Decimal:
    """Calculate the total amount of all expenses."""
    with get_session() as session:
        statement = select(Expense)
        expenses = session.exec(statement).all()
        total = sum(expense.amount for expense in expenses)
        return total if isinstance(total, Decimal) else Decimal("0")
