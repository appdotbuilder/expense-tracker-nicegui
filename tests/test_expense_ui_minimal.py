import pytest
from decimal import Decimal
from datetime import date
from nicegui.testing import User
from app.database import reset_db
from app.expense_service import create_expense, get_all_expenses
from app.models import ExpenseCreate


@pytest.fixture()
def new_db():
    reset_db()
    yield
    reset_db()


async def test_basic_page_loads(user: User, new_db) -> None:
    """Test that the basic page loads."""
    await user.open("/")

    # Check page title
    await user.should_see("💰 Expense Tracker")


async def test_get_all_expenses_direct(new_db) -> None:
    """Test that get_all_expenses works directly."""
    # Create test expense
    create_expense(ExpenseCreate(description="Test", amount=Decimal("10.00"), date=date(2024, 1, 15)))

    expenses = get_all_expenses()
    assert len(expenses) == 1
    assert expenses[0].description == "Test"


async def test_expense_is_created_before_page_load(user: User, new_db) -> None:
    """Test that expense created before page load is visible."""
    # Create expense before opening page
    create_expense(ExpenseCreate(description="Before Load", amount=Decimal("25.00"), date=date(2024, 1, 15)))

    # Verify expense exists
    expenses = get_all_expenses()
    assert len(expenses) == 1

    # Open page
    await user.open("/")

    # Check that expense is displayed
    await user.should_see("Before Load")
    await user.should_see("Total: $25.00")
