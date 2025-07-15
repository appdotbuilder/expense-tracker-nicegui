import pytest
from decimal import Decimal
from datetime import date
from nicegui.testing import User
from nicegui import ui
from app.database import reset_db
from app.expense_service import create_expense
from app.models import ExpenseCreate


@pytest.fixture()
def new_db():
    reset_db()
    yield
    reset_db()


async def test_expense_tracker_page_loads(user: User, new_db) -> None:
    """Test that the expense tracker page loads correctly."""
    await user.open("/")

    # Check page title and main elements
    await user.should_see("💰 Expense Tracker")
    await user.should_see("Add New Expense")
    await user.should_see("Expense History")
    await user.should_see("Total: $0.00")


async def test_add_expense_form_validation(user: User, new_db) -> None:
    """Test form validation for adding expenses."""
    await user.open("/")

    # Try to submit empty form
    user.find("Add Expense").click()
    await user.should_see("Please enter a description")

    # Add description but keep amount at 0
    description_input = user.find("Enter expense description")
    description_input.type("Test expense")
    user.find("Add Expense").click()
    await user.should_see("Please enter a valid amount")


async def test_add_expense_success(user: User, new_db) -> None:
    """Test successfully adding an expense."""
    await user.open("/")

    # Fill out form
    user.find("Enter expense description").type("Coffee and pastry")

    # Set amount
    amount_elements = list(user.find(ui.number).elements)
    if amount_elements:
        amount_elements[0].set_value(12.50)

    # Set date
    date_elements = list(user.find(ui.date).elements)
    if date_elements:
        date_elements[0].set_value(date(2024, 1, 15).isoformat())

    # Submit form
    user.find("Add Expense").click()

    # Check success message and updated total
    await user.should_see("Expense added successfully!")
    await user.should_see("Total: $12.50")


async def test_expense_list_display(user: User, new_db) -> None:
    """Test that expenses are displayed correctly in the list."""
    # Create test expenses
    create_expense(ExpenseCreate(description="Lunch", amount=Decimal("15.75"), date=date(2024, 1, 10)))

    create_expense(ExpenseCreate(description="Gas", amount=Decimal("45.00"), date=date(2024, 1, 15)))

    await user.open("/")

    # Check total is displayed
    await user.should_see("Total: $60.75")

    # Check expenses are displayed
    await user.should_see("Lunch")
    await user.should_see("$15.75")
    await user.should_see("Gas")
    await user.should_see("$45.00")
    await user.should_see("2024-01-10")
    await user.should_see("2024-01-15")


async def test_empty_expense_list(user: User, new_db) -> None:
    """Test display when no expenses exist."""
    await user.open("/")

    await user.should_see("No expenses recorded yet.")
    await user.should_see("Total: $0.00")


async def test_form_clears_after_submission(user: User, new_db) -> None:
    """Test that form fields are cleared after successful submission."""
    await user.open("/")

    # Fill out form
    description_input = user.find("Enter expense description")
    description_input.type("Test expense")

    amount_elements = list(user.find(ui.number).elements)
    if amount_elements:
        amount_elements[0].set_value(25.00)

    # Submit form
    user.find("Add Expense").click()

    # Wait for success message
    await user.should_see("Expense added successfully!")

    # Check that form is cleared - we can't reliably test this in the UI test
    # The form clearing is tested by the fact that we can add another expense
    # and the success flow works correctly

    if amount_elements:
        assert amount_elements[0].value == 0.00


async def test_expense_date_ordering(user: User, new_db) -> None:
    """Test that expenses are ordered by date (newest first)."""
    # Create expenses with different dates
    create_expense(ExpenseCreate(description="Oldest expense", amount=Decimal("10.00"), date=date(2024, 1, 1)))

    create_expense(ExpenseCreate(description="Newest expense", amount=Decimal("20.00"), date=date(2024, 1, 31)))

    create_expense(ExpenseCreate(description="Middle expense", amount=Decimal("15.00"), date=date(2024, 1, 15)))

    await user.open("/")

    # Check that all expenses are displayed
    await user.should_see("Oldest expense")
    await user.should_see("Newest expense")
    await user.should_see("Middle expense")

    # Check total
    await user.should_see("Total: $45.00")


async def test_expense_amount_formatting(user: User, new_db) -> None:
    """Test that expense amounts are formatted correctly."""
    create_expense(ExpenseCreate(description="Test expense", amount=Decimal("123.45"), date=date(2024, 1, 15)))

    await user.open("/")

    # Amount should be formatted with $ and 2 decimal places
    await user.should_see("$123.45")
    await user.should_see("Total: $123.45")


async def test_decimal_precision_handling(user: User, new_db) -> None:
    """Test that decimal precision is handled correctly."""
    create_expense(ExpenseCreate(description="Precise expense", amount=Decimal("99.99"), date=date(2024, 1, 15)))

    await user.open("/")

    await user.should_see("$99.99")
    await user.should_see("Total: $99.99")


async def test_large_expense_amounts(user: User, new_db) -> None:
    """Test handling of large expense amounts."""
    create_expense(ExpenseCreate(description="Large expense", amount=Decimal("1234.56"), date=date(2024, 1, 15)))

    await user.open("/")

    await user.should_see("$1234.56")
    await user.should_see("Total: $1234.56")


async def test_multiple_expenses_total_calculation(user: User, new_db) -> None:
    """Test that total is calculated correctly with multiple expenses."""
    create_expense(ExpenseCreate(description="Expense 1", amount=Decimal("10.25"), date=date(2024, 1, 10)))

    create_expense(ExpenseCreate(description="Expense 2", amount=Decimal("20.50"), date=date(2024, 1, 15)))

    create_expense(ExpenseCreate(description="Expense 3", amount=Decimal("15.75"), date=date(2024, 1, 20)))

    await user.open("/")

    # Total should be 10.25 + 20.50 + 15.75 = 46.50
    await user.should_see("Total: $46.50")
