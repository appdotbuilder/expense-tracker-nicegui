import pytest
from decimal import Decimal
from datetime import date
from app.expense_service import create_expense, get_all_expenses, get_expense_by_id, delete_expense, get_total_expenses
from app.models import ExpenseCreate
from app.database import reset_db


@pytest.fixture()
def new_db():
    reset_db()
    yield
    reset_db()


def test_create_expense(new_db):
    """Test creating a new expense."""
    expense_data = ExpenseCreate(description="Lunch at restaurant", amount=Decimal("25.50"), date=date(2024, 1, 15))

    expense = create_expense(expense_data)

    assert expense.id is not None
    assert expense.description == "Lunch at restaurant"
    assert expense.amount == Decimal("25.50")
    assert expense.date == date(2024, 1, 15)
    assert expense.created_at is not None


def test_get_all_expenses_empty(new_db):
    """Test getting expenses when database is empty."""
    expenses = get_all_expenses()
    assert expenses == []


def test_get_all_expenses_with_data(new_db):
    """Test getting all expenses with data."""
    # Create test expenses
    expense1 = create_expense(ExpenseCreate(description="Coffee", amount=Decimal("5.00"), date=date(2024, 1, 10)))

    expense2 = create_expense(ExpenseCreate(description="Dinner", amount=Decimal("30.00"), date=date(2024, 1, 15)))

    expenses = get_all_expenses()

    assert len(expenses) == 2
    # Should be ordered by date desc (newest first)
    assert expenses[0].id == expense2.id
    assert expenses[1].id == expense1.id


def test_get_expense_by_id_exists(new_db):
    """Test getting expense by ID when it exists."""
    expense = create_expense(ExpenseCreate(description="Gas", amount=Decimal("45.00"), date=date(2024, 1, 20)))

    if expense.id is not None:
        retrieved = get_expense_by_id(expense.id)

        assert retrieved is not None
        assert retrieved.id == expense.id
        assert retrieved.description == "Gas"
        assert retrieved.amount == Decimal("45.00")


def test_get_expense_by_id_not_exists(new_db):
    """Test getting expense by ID when it doesn't exist."""
    retrieved = get_expense_by_id(999)
    assert retrieved is None


def test_delete_expense_exists(new_db):
    """Test deleting an expense that exists."""
    expense = create_expense(ExpenseCreate(description="Groceries", amount=Decimal("75.25"), date=date(2024, 1, 25)))

    if expense.id is not None:
        result = delete_expense(expense.id)

        assert result is True

        # Verify it's actually deleted
        retrieved = get_expense_by_id(expense.id)
        assert retrieved is None


def test_delete_expense_not_exists(new_db):
    """Test deleting an expense that doesn't exist."""
    result = delete_expense(999)
    assert result is False


def test_get_total_expenses_empty(new_db):
    """Test getting total expenses when database is empty."""
    total = get_total_expenses()
    assert total == Decimal("0")


def test_get_total_expenses_with_data(new_db):
    """Test calculating total expenses with data."""
    create_expense(ExpenseCreate(description="Item 1", amount=Decimal("10.50"), date=date(2024, 1, 1)))

    create_expense(ExpenseCreate(description="Item 2", amount=Decimal("25.75"), date=date(2024, 1, 2)))

    create_expense(ExpenseCreate(description="Item 3", amount=Decimal("15.25"), date=date(2024, 1, 3)))

    total = get_total_expenses()
    assert total == Decimal("51.50")


def test_create_expense_with_zero_amount(new_db):
    """Test creating expense with zero amount - should work."""
    expense_data = ExpenseCreate(description="Free sample", amount=Decimal("0.00"), date=date(2024, 1, 15))

    expense = create_expense(expense_data)
    assert expense.amount == Decimal("0.00")


def test_create_expense_with_long_description(new_db):
    """Test creating expense with maximum length description."""
    long_description = "A" * 500  # Max length from model
    expense_data = ExpenseCreate(description=long_description, amount=Decimal("10.00"), date=date(2024, 1, 15))

    expense = create_expense(expense_data)
    assert expense.description == long_description


def test_create_expense_with_future_date(new_db):
    """Test creating expense with future date."""
    future_date = date(2025, 12, 31)
    expense_data = ExpenseCreate(description="Future expense", amount=Decimal("100.00"), date=future_date)

    expense = create_expense(expense_data)
    assert expense.date == future_date


def test_expense_ordering_by_date(new_db):
    """Test that expenses are ordered by date descending."""
    # Create expenses with different dates
    expense1 = create_expense(ExpenseCreate(description="Oldest", amount=Decimal("10.00"), date=date(2024, 1, 1)))

    expense2 = create_expense(ExpenseCreate(description="Newest", amount=Decimal("20.00"), date=date(2024, 1, 31)))

    expense3 = create_expense(ExpenseCreate(description="Middle", amount=Decimal("15.00"), date=date(2024, 1, 15)))

    expenses = get_all_expenses()

    # Should be ordered by date desc
    assert expenses[0].id == expense2.id  # Newest first
    assert expenses[1].id == expense3.id  # Middle
    assert expenses[2].id == expense1.id  # Oldest last
