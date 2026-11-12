import json
import re
from pathlib import Path


# STEP 1: Read OCR layout data

BASE_DIR = Path(__file__).resolve().parent

input_file = BASE_DIR / "local_data" / "ocr" / "receipt_layout.json"

ocr_data = json.loads(input_file.read_text(encoding="utf-8"))


# STEP 2: Calculate the vertical center of a text box

def get_center_y(box):
    return (box[1] + box[3]) / 2


# STEP 3: Separate products and prices

products = []
prices = []

for entry in ocr_data:

    text = entry["text"].strip()

    # Match Costco product ID followed by product name
    product_match = re.match(r"^(\d{3,8})\s+(.+)$", text)

    # Match prices such as 14.99 or 3.97 A
    price_match = re.fullmatch(r"(\d+\.\d{2})(?:\s+[A-Z])?", text)

    if product_match:

        products.append({
            "product_id": product_match.group(1),
            "name": product_match.group(2),
            "box": entry["box"]
        })

    elif price_match:

        prices.append({
            "amount": float(price_match.group(1)),
            "box": entry["box"]
        })


# STEP 4: Match products to nearby prices

matched_items = []

used_prices = set()

for product in products:

    product_y = get_center_y(product["box"])

    candidates = []

    for index, price in enumerate(prices):

        if index in used_prices:
            continue

        price_y = get_center_y(price["box"])

        vertical_distance = abs(product_y - price_y)

        # Price should be to the right of product
        is_right = price["box"][0] > product["box"][2] + 20

        # Product and price should be on approximately the same row
        if vertical_distance <= 25 and is_right:

            candidates.append((vertical_distance, index, price))

    if candidates:

        # Select the price closest to the product's vertical center
        candidates.sort(key=lambda item: item[0])

        distance, price_index, selected_price = candidates[0]

        used_prices.add(price_index)

        line_total = selected_price["amount"]

    else:

        line_total = None

    matched_items.append({
        "product_id": product["product_id"],
        "name": product["name"],
        "line_total": line_total
    })


# STEP 5: Display results

print("\nMATCHED RECEIPT ITEMS")
print("-" * 55)

for item in matched_items:

    print(f"{item['name']:<25} {item['line_total']}")


# STEP 6: Save matched data

output_file = BASE_DIR / "local_data" / "ocr" / "row_matches.json"

output_file.write_text(
    json.dumps(matched_items, indent=2),
    encoding="utf-8"
)

print("\nMatched receipt data saved successfully!")
  