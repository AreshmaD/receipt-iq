import sqlite3
from pathlib import Path

# Step 1: Define database location
BASE_DIR = Path(__file__).resolve().parent

DB_PATH = BASE_DIR / "local_data" / "receiptiq.db"

DB_PATH.parent.mkdir(parents=True, exist_ok=True)


# Step 2: Connect to SQLite
conn = sqlite3.connect(DB_PATH)

try:
    # Enable foreign key relationships
    conn.execute("PRAGMA foreign_keys = ON")

    # Step 3: Create the receipts table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            merchant TEXT,
            purchase_date TEXT,
            subtotal_cents INTEGER,
            tax_cents INTEGER,
            total_cents INTEGER,
            status TEXT NOT NULL DEFAULT 'needs_review',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Step 4: Create the receipt_items table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS receipt_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            receipt_id INTEGER NOT NULL,
            product_code TEXT,
            name TEXT NOT NULL,
            original_price_cents INTEGER,
            discount_cents INTEGER NOT NULL DEFAULT 0,
            final_price_cents INTEGER,

            FOREIGN KEY (receipt_id)
                REFERENCES receipts(id)
                ON DELETE CASCADE
        )
    """)

    # Step 5: Save database changes
    conn.commit()

    print("Database created successfully!")

    # Step 6: Display database tables
    tables = conn.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """).fetchall()

    print("\nDatabase tables:")

    for table in tables:
        print("-", table[0])

finally:
    conn.close()