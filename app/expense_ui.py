from decimal import Decimal
from datetime import date
from nicegui import ui
from app.expense_service import create_expense, get_all_expenses, delete_expense, get_total_expenses
from app.models import ExpenseCreate


def create():
    """Create the expense tracking UI."""

    @ui.page("/")
    def expense_tracker():
        # Apply modern theme
        ui.colors(
            primary="#2563eb",
            secondary="#64748b",
            accent="#10b981",
            positive="#10b981",
            negative="#ef4444",
            warning="#f59e0b",
            info="#3b82f6",
        )

        # Page header
        with ui.row().classes("w-full justify-between items-center mb-8"):
            ui.label("💰 Expense Tracker").classes("text-3xl font-bold text-gray-800")
            total_label = ui.label("Total: $0.00").classes("text-lg font-semibold text-gray-600")

        # Main content container
        with ui.row().classes("w-full gap-8"):
            # Left column - Add expense form
            with ui.column().classes("w-96"):
                with ui.card().classes("w-full p-6 shadow-lg rounded-lg"):
                    ui.label("Add New Expense").classes("text-xl font-bold mb-6 text-gray-800")

                    # Form fields
                    ui.label("Description").classes("text-sm font-medium text-gray-700 mb-1")
                    description_input = ui.input(placeholder="Enter expense description").classes("w-full mb-4")

                    ui.label("Amount ($)").classes("text-sm font-medium text-gray-700 mb-1")
                    amount_input = ui.number(value=0.00, format="%.2f", step=0.01, min=0.01).classes("w-full mb-4")

                    ui.label("Date").classes("text-sm font-medium text-gray-700 mb-1")
                    date_input = ui.date(value=date.today().isoformat()).classes("w-full mb-6")

                    # Submit button (defined after refresh_data)
                    add_button = ui.button("Add Expense").classes(
                        "w-full bg-primary text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors"
                    )

            # Right column - Expense list
            with ui.column().classes("flex-1"):
                with ui.card().classes("w-full p-6 shadow-lg rounded-lg"):
                    ui.label("Expense History").classes("text-xl font-bold mb-6 text-gray-800")

                    # Table container
                    table_container = ui.column().classes("w-full")

        # Function to refresh all data
        def refresh_data():
            total = get_total_expenses()
            total_label.text = f"Total: ${total:.2f}"
            refresh_expense_list(table_container, refresh_data)

        # Add expense function
        def add_expense():
            try:
                if not description_input.value or not description_input.value.strip():
                    ui.notify("Please enter a description", type="negative")
                    return

                if not amount_input.value or amount_input.value <= 0:
                    ui.notify("Please enter a valid amount", type="negative")
                    return

                expense_data = ExpenseCreate(
                    description=description_input.value.strip(),
                    amount=Decimal(str(amount_input.value)),
                    date=date_input.value,
                )

                create_expense(expense_data)

                # Clear form
                description_input.value = ""
                amount_input.value = 0.00
                date_input.value = date.today().isoformat()

                # Refresh data
                refresh_data()

                ui.notify("Expense added successfully!", type="positive")

            except Exception as e:
                ui.notify(f"Error adding expense: {str(e)}", type="negative")

        # Connect the button to the add_expense function
        add_button.on_click(add_expense)

        # Initial load
        refresh_data()


def refresh_expense_list(table_container, refresh_callback):
    """Refresh the expense list display."""
    table_container.clear()
    expenses = get_all_expenses()

    with table_container:
        if not expenses:
            ui.label("No expenses recorded yet.").classes("text-gray-500 text-center py-8")
            return

        # Simple list display for testing
        for expense in expenses:
            with ui.card().classes("w-full p-4 mb-2 bg-white shadow-sm"):
                with ui.row().classes("w-full justify-between items-center"):
                    with ui.column().classes("flex-1"):
                        ui.label(expense.description).classes("font-medium")
                        ui.label(expense.date.strftime("%Y-%m-%d")).classes("text-sm text-gray-500")
                    with ui.column().classes("items-end"):
                        ui.label(f"${expense.amount:.2f}").classes("text-lg font-bold")
                        if expense.id is not None:
                            ui.button(
                                "Delete",
                                on_click=lambda e, expense_id=expense.id: handle_delete_expense(
                                    expense_id, refresh_callback
                                )
                                if expense_id
                                else None,
                            ).classes("text-sm").props("color=negative size=sm")


def handle_delete_expense(expense_id: int, refresh_callback):
    """Handle deleting an expense."""
    if delete_expense(expense_id):
        ui.notify("Expense deleted successfully!", type="positive")
        refresh_callback()
    else:
        ui.notify("Error deleting expense", type="negative")
