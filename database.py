
import sqlite3
from pathlib import Path

DB_FILE = Path(__file__).resolve().parent / "expenses.db"


def get_connection():
    """Create a connection to the SQLite database."""
    return sqlite3.connect(DB_FILE)



def initialize_database():
    """Create the expenses and budgets tables if needed."""
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL CHECK (amount > 0),
                description TEXT DEFAULT ''
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                month TEXT PRIMARY KEY,
                amount REAL NOT NULL CHECK (amount > 0)
            )
        """)

def add_expense(date, category, amount, description):
    """Save a new expense in SQLite."""
    with get_connection() as connection:
        connection.execute("""
            INSERT INTO expenses (date, category, amount, description)
            VALUES (?, ?, ?, ?)
        """, (date, category, amount, description))


def get_expenses():
    """Return all expenses as dictionaries."""
    with get_connection() as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute("""
            SELECT id, date, category, amount, description
            FROM expenses
            ORDER BY id DESC
        """).fetchall()

    return [dict(row) for row in rows]


def update_expense(expense_id, date, category, amount, description):
    """Update an existing expense using its ID."""
    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    with get_connection() as connection:
        cursor = connection.execute("""
            UPDATE expenses
            SET date = ?, category = ?, amount = ?, description = ?
            WHERE id = ?
        """, (date, category, amount, description, expense_id))

        return cursor.rowcount > 0


def delete_expense(expense_id):
    """Delete an expense using its ID."""
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM expenses WHERE id = ?",
            (expense_id,)
        )

        return cursor.rowcount > 0


def set_monthly_budget(month, amount):
    """Save or update a budget for a month.

    month format: YYYY-MM
    """
    if amount <= 0:
        raise ValueError("Budget must be greater than zero.")

    with get_connection() as connection:
        connection.execute("""
            INSERT INTO budgets (month, amount)
            VALUES (?, ?)
            ON CONFLICT(month)
            DO UPDATE SET amount = excluded.amount
        """, (month, amount))


def get_monthly_budget(month):
    """Return the saved budget for a month, or None."""
    with get_connection() as connection:
        row = connection.execute(
            "SELECT amount FROM budgets WHERE month = ?",
            (month,)
        ).fetchone()

    return row[0] if row else None


def get_monthly_expense_total(month):
    """Calculate total expenses for a month.

    month format: YYYY-MM
    expense dates are stored as DD-MM-YYYY.
    """
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT date, amount
            FROM expenses
        """).fetchall()

    total = 0.0

    for date_text, amount in rows:
        try:
            from datetime import datetime

            expense_date = datetime.strptime(
                date_text.strip(), "%d-%m-%Y"
            )

            if expense_date.strftime("%Y-%m") == month:
                total += amount

        except (ValueError, TypeError):
            # Ignore expenses with invalid or unsupported date formats.
            continue

    return total
