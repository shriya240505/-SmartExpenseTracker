
import csv
import sqlite3
from pathlib import Path


# Keep all data files inside the project folder
BASE_DIR = Path(__file__).resolve().parent
TEXT_FILE = BASE_DIR / "expenses.txt"
DB_FILE = BASE_DIR / "expenses.db"


def migrate_data():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    # Create the expenses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL CHECK (amount > 0),
            description TEXT DEFAULT ''
        )
    """)

    # Prevent accidental duplicate imports
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS migration_log (
            source TEXT PRIMARY KEY
        )
    """)

    cursor.execute(
        "SELECT source FROM migration_log WHERE source = ?",
        ("expenses.txt",)
    )

    if cursor.fetchone():
        print("Migration already completed. No data imported again.")
        connection.close()
        return

    imported_count = 0

    if TEXT_FILE.exists():
        with TEXT_FILE.open("r", encoding="utf-8", newline="") as file:
            reader = csv.reader(file)

            for row in reader:
                if len(row) != 4:
                    continue

                date, category, amount_text, description = row

                try:
                    amount = float(amount_text)
                except ValueError:
                    continue

                if amount <= 0 or not date.strip() or not category.strip():
                    continue

                cursor.execute("""
                    INSERT INTO expenses
                    (date, category, amount, description)
                    VALUES (?, ?, ?, ?)
                """, (date.strip(), category.strip(), amount, description.strip()))

                imported_count += 1

    cursor.execute(
        "INSERT INTO migration_log (source) VALUES (?)",
        ("expenses.txt",)
    )

    connection.commit()
    connection.close()

    print("Database created successfully!")
    print(f"Expenses imported: {imported_count}")
    print(f"Database location: {DB_FILE}")


if __name__ == "__main__":
    migrate_data()
