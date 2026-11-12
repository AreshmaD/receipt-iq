
import sqlite3
from pathlib import Path
from decimal import Decimal
from contextlib import closing


# STEP 1: Locate the SQLite database

BASE_DIR = Path(__file__).resolve().parent

DB_PATH = BASE_DIR / "local_data" / "receiptiq.db"


# STEP 2: Convert cents into dollars

def format_money(cents):

    if cents is None:
        return "Unknown"

    dollars = Decimal(cents) / 100

    return f"${dollars:.2f}"


# STEP 3: Connect to the database

with closing(sqlite3.connect(DB_PATH)) as conn:

    conn.row_factory = sqlite3.Row

    # STEP 4: Find the latest receipt

    latest_receipt = conn.execute("""
        SELECT id
        FROM receipts
        ORDER BY id DESC
        LIMIT 1
    """).fetchone()

    if latest_receipt is None:
        print("No receipts found.")

    else:

        receipt_id = latest_receipt["id"]

        # STEP 5: Join receipts and receipt_items

        rows = conn.execute("""
            SELECT
                r.id AS receipt_id,
                r.merchant,
                r.purchase_date,
                r.total_cents,
                r.status,
                i.product_code,
                i.name,
                i.original_price_cents,
                i.discount_cents,
                i.final_price_cents

            FROM receipts AS r

            JOIN receipt_items AS i
                ON r.id = i.receipt_id

            WHERE r.id = ?

            ORDER BY i.id

        """, (receipt_id,)).fetchall()


        # STEP 6: Display results

        print("\nRECEIPT DETAILS")
        print("-" * 55)

        if rows:

            print("Receipt ID:", rows[0]["receipt_id"])
            print("Merchant:", rows[0]["merchant"])
            print("Date:", rows[0]["purchase_date"])
            print("Total:", format_money(rows[0]["total_cents"]))
            print("Status:", rows[0]["status"])

            print("\nPURCHASED ITEMS")
            print("-" * 55)

            for row in rows:

                print(
                    f"{row['name']:<25}"
                    f"{format_money(row['final_price_cents'])}"
                )

            print("-" * 55)
            print("Total items:", len(rows))

        else:
            print("No matching receipt items found.")