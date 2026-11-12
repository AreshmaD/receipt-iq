import sqlite3
from pathlib import Path
from contextlib import closing
from decimal import Decimal


# STEP 1: Locate our database

BASE_DIR = Path(__file__).resolve().parent

DB_PATH = BASE_DIR / "local_data" / "receiptiq.db"

if not DB_PATH.exists():
    raise FileNotFoundError("ReceiptIQ database not found!")


# STEP 2: Convert cents into dollars

def format_money(cents):

    if cents is None:
        return "Unknown"

    dollars = Decimal(cents) / 100

    return f"${dollars:.2f}"


# STEP 3: Connect to SQLite

with closing(sqlite3.connect(DB_PATH)) as conn:

    # Access database columns by name
    conn.row_factory = sqlite3.Row

    # STEP 4: Retrieve the most recently inserted receipt

    receipt = conn.execute("""
        SELECT
            id,
            merchant,
            purchase_date,
            subtotal_cents,
            tax_cents,
            total_cents,
            status
        FROM receipts
        ORDER BY id DESC
        LIMIT 1
    """).fetchone()

    if receipt is None:
        print("No receipts found in database.")

    else:

        # STEP 5: Display receipt information

        print("\nRECEIPT INFORMATION")
        print("-" * 45)

        print("Receipt ID:", receipt["id"])
        print("Merchant:", receipt["merchant"])
        print("Date:", receipt["purchase_date"])
        print("Subtotal:", format_money(receipt["subtotal_cents"]))
        print("Tax:", format_money(receipt["tax_cents"]))
        print("Total:", format_money(receipt["total_cents"]))
        print("Status:", receipt["status"])

        # STEP 6: Retrieve products belonging to this receipt

        items = conn.execute("""
            SELECT
                product_code,
                name,
                original_price_cents,
                discount_cents,
                final_price_cents
            FROM receipt_items
            WHERE receipt_id = ?
            ORDER BY id
        """, (receipt["id"],)).fetchall()

        # STEP 7: Display products

        print("\nPURCHASED ITEMS")
        print("-" * 45)

        for item in items:

            print(
                f"{item['name']:<22}"
                f"{format_money(item['final_price_cents'])}"
            )

        print("\nTotal products:", len(items))