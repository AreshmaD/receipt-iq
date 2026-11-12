import json
import re
from decimal import Decimal
from pathlib import Path

# Step 1: Locate the backend folder
BASE_DIR = Path(__file__).resolve().parent

# Step 2: Load our existing OCR results
ocr_file = BASE_DIR / "local_data" / "ocr" / "receipt_layout.json"

items_file = BASE_DIR / "local_data" / "ocr" / "row_matches.json"

ocr_data = json.loads(ocr_file.read_text(encoding="utf-8"))
items = json.loads(items_file.read_text(encoding="utf-8"))


# Step 3: Find discounts
discounts = []

for entry in ocr_data:

    text = entry["text"].strip()

    # Match discounts such as 3.00- or 2.00-
    match = re.fullmatch(r"(\d+\.\d{2})-", text)

    if match:
        discount = Decimal(match.group(1))
        discounts.append(discount)


# Step 4: Calculate total product prices
product_total = sum(
    Decimal(str(item["line_total"]))
    for item in items
    if item["line_total"] is not None
)

# Step 5: Calculate total discounts
total_discount = sum(discounts, Decimal("0.00"))

# Step 6: Calculate adjusted subtotal
calculated_subtotal = product_total - total_discount


# Step 7: Display results
print("\nRECEIPT CALCULATION")
print("-------------------------")

print("Products:", len(items))
print("Product total: $", product_total)
print("Discounts found:", len(discounts))
print("Total discounts: $", total_discount)
print("Calculated subtotal: $", calculated_subtotal)