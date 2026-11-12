
import json
import sqlite3

from pathlib import Path
from decimal import Decimal
from contextlib import closing


# STEP 1: Define file locations

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "local_data"

DB_PATH = DATA_DIR / "receiptiq.db"

receipt_file = DATA_DIR / "structured" / "receipt.json"

items_file = DATA_DIR / "ocr" / "items_with_discounts.json"

validation_file = DATA_DIR / "structured" / "validation_report.json"


# STEP 2: Load JSON data

receipt = json.loads(
    receipt_file.read_text(encoding="utf-8")
)

items = json.loads(
    items_file.read_text(encoding="utf-8")
)

validation = json.loads(
    validation_file.read_text(encoding="utf-8")
)


# STEP 3: Convert dollar amounts to cents

def to_cents(value):

    if value is None:
        return None

    amount = Decimal(str(value))

    cents = amount * 100

    if cents != cents.to_integral_value():
        raise ValueError(f"Invalid currency amount: {value}")

    return int(cents)


# STEP 4: Check validation results

if validation.get("financial_checks_passed") is not True:
    raise ValueError(
        "Receipt failed financial validation. Review it before saving."
    )

if not items:
    raise ValueError("No receipt items found.")


# STEP 5: Connect to SQLite

if not DB_PATH.exists():
    raise FileNotFoundError(
        "Database not found. Run step6_create_database.py first."
    )

with closing(sqlite3.connect(DB_PATH)) as conn:

    conn.execute("PRAGMA foreign_keys = ON")

    # Save receipt and items in one transaction
    with conn:

        # STEP 6: Insert receipt information

        cursor = conn.execute(
            """
            INSERT INTO receipts (
                merchant,
                purchase_date,
                subtotal_cents,
                tax_cents,
                total_cents,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                receipt.get("merchant"),
                receipt.get("date"),
                to_cents(receipt.get("subtotal")),
                to_cents(receipt.get("tax")),
                to_cents(receipt.get("total")),
                "needs_review"
            )
        )

        # Get the newly created receipt ID
        receipt_id = cursor.lastrowid

        # STEP 7: Insert individual products

        for item in items:

            conn.execute(
                """
                INSERT INTO receipt_items (
                    receipt_id,
                    product_code,
                    name,
                    original_price_cents,
                    discount_cents,
                    final_price_cents
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    receipt_id,
                    item["product_id"],
                    item["name"],
                    to_cents(item["original_price"]),
                    to_cents(item["discount"]),
                    to_cents(item["final_price"])
                )
            )


# STEP 8: Display results

print("\nRECEIPT SAVED SUCCESSFULLY!")
print("-" * 40)

print("Receipt ID:", receipt_id)
print("Merchant:", receipt.get("merchant"))
print("Purchase Date:", receipt.get("date"))
print("Products Saved:", len(items))
print("Total:", receipt.get("total"))
print("Status: needs_review")