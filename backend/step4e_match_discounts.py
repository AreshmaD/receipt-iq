import json
import re
from pathlib import Path
from decimal import Decimal

# Step 1: Locate existing files
BASE_DIR = Path(__file__).resolve().parent
OCR_DIR = BASE_DIR / "local_data" / "ocr"

ocr_data = json.loads(
    (OCR_DIR / "receipt_layout.json").read_text(encoding="utf-8")
)

items = json.loads(
    (OCR_DIR / "row_matches.json").read_text(encoding="utf-8")
)


# Step 2: Calculate vertical center
def center_y(box):
    return (box[1] + box[3]) / 2


# Step 3: Find product positions
products = []

for entry in ocr_data:
    text = entry["text"].strip()

    match = re.match(r"^(\d{3,8})\s+(.+)$", text)

    if match:
        products.append({
            "product_id": match.group(1),
            "name": match.group(2),
            "y": center_y(entry["box"]),
            "box": entry["box"]
        })


# Step 4: Verify products match our previous results
if len(products) != len(items):
    raise ValueError("Product counts do not match!")

for product, item in zip(products, items):
    if (
        product["product_id"] != item["product_id"]
        or product["name"] != item["name"]
    ):
        raise ValueError("Product order does not match!")


# Step 5: Find and match discounts
product_discounts = {
    index: Decimal("0.00")
    for index in range(len(products))
}

unmatched_discounts = []

for entry in ocr_data:

    text = entry["text"].strip()

    match = re.fullmatch(r"(\d+\.\d{2})-", text)

    if not match:
        continue

    discount = Decimal(match.group(1))
    discount_y = center_y(entry["box"])

    candidates = []

    for index, product in enumerate(products):

        product_y = product["y"]

        # Find next product position
        if index + 1 < len(products):
            next_y = products[index + 1]["y"]
        else:
            next_y = float("inf")

        # Check discount location
        below_product = product_y < discount_y < next_y

        close_enough = discount_y - product_y <= 80

        on_right = entry["box"][0] > product["box"][2]

        if below_product and close_enough and on_right:
            candidates.append(index)

    # Assign only when we find one clear match
    if len(candidates) == 1:
        product_discounts[candidates[0]] += discount
    else:
        unmatched_discounts.append(text)


# Step 6: Calculate final prices
final_items = []

for index, item in enumerate(items):

    if item["line_total"] is None:
        original_price = None
        final_price = None
    else:
        original_price = Decimal(str(item["line_total"]))
        final_price = original_price - product_discounts[index]

    final_items.append({
        "product_id": item["product_id"],
        "name": item["name"],
        "original_price": (
            str(original_price) if original_price is not None else None
        ),
        "discount": str(product_discounts[index]),
        "final_price": (
            str(final_price) if final_price is not None else None
        )
    })


# Step 7: Display discounted items
print("\nDISCOUNTED PRODUCTS")
print("-" * 60)

for item in final_items:

    if Decimal(item["discount"]) > 0:
        print(
            f"{item['name']:<20}"
            f"Original: ${item['original_price']}  "
            f"Discount: ${item['discount']}  "
            f"Final: ${item['final_price']}"
        )


# Step 8: Calculate subtotal
calculated_subtotal = sum(
    (
        Decimal(item["final_price"])
        for item in final_items
        if item["final_price"] is not None
    ),
    Decimal("0.00")
)

print("\nCalculated subtotal:", calculated_subtotal)
print("Unmatched discounts:", unmatched_discounts)


# Step 9: Save the results
output_file = OCR_DIR / "items_with_discounts.json"

output_file.write_text(
    json.dumps(final_items, indent=2),
    encoding="utf-8"
)

print("\nItems with discounts saved successfully!")