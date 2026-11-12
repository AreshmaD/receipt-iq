import json
from pathlib import Path
from decimal import Decimal

# STEP 1: Locate our project files

BASE_DIR = Path(__file__).resolve().parent

items_file = BASE_DIR / "local_data" / "ocr" / "items_with_discounts.json"

receipt_file = BASE_DIR / "local_data" / "structured" / "receipt.json"


# STEP 2: Load extracted data

items = json.loads(items_file.read_text(encoding="utf-8"))

receipt = json.loads(receipt_file.read_text(encoding="utf-8"))


# STEP 3: Validate individual product calculations

calculated_subtotal = Decimal("0.00")

errors = []

for item in items:

    name = item["name"]

    original = item["original_price"]
    discount = item["discount"]
    final = item["final_price"]

    # Check for missing prices
    if original is None or discount is None or final is None:
        errors.append(f"Missing price information: {name}")
        continue

    # Convert values to Decimal
    original = Decimal(str(original))
    discount = Decimal(str(discount))
    final = Decimal(str(final))

    # Check for invalid amounts
    if original < 0 or discount < 0 or discount > original:
        errors.append(f"Invalid price or discount: {name}")

    # Check individual product calculation
    if original - discount != final:
        errors.append(f"Incorrect final price: {name}")

    calculated_subtotal += final


# STEP 4: Compare against receipt subtotal

receipt_subtotal = receipt.get("subtotal")

if receipt_subtotal is None:
    errors.append("Receipt subtotal is missing")

else:
    receipt_subtotal = Decimal(str(receipt_subtotal))

    if calculated_subtotal != receipt_subtotal:
        errors.append("Subtotal does not match")

# STEP 5: Validate tax and grand total

receipt_tax = receipt.get("tax")
receipt_total = receipt.get("total")

# Check for missing values
if (
    receipt_subtotal is None
    or receipt_tax is None
    or receipt_total is None
):
    errors.append("Missing subtotal, tax, or total")

else:
    # Convert values to Decimal
    receipt_tax = Decimal(str(receipt_tax))
    receipt_total = Decimal(str(receipt_total))

    # Calculate expected total
    expected_total = receipt_subtotal + receipt_tax

    # Compare calculated and extracted totals
    if expected_total != receipt_total:
        errors.append(
            f"Total mismatch: Expected ${expected_total}, "
            f"but found ${receipt_total}"
        )

    else:
        print("\nGrand total validation: PASSED")
        print("Subtotal:", receipt_subtotal)
        print("Tax:", receipt_tax)
        print("Calculated total:", expected_total)
        print("Receipt total:", receipt_total)


# STEP 5: Display validation results

print("\nRECEIPT VALIDATION REPORT")
print("-" * 40)

print("Products:", len(items))
print("Calculated subtotal:", calculated_subtotal)
print("Receipt subtotal:", receipt_subtotal)

if errors:
    print("\nVALIDATION: FAILED")

    for error in errors:
        print("-", error)

else:
    print("\nFINANCIAL CHECKS: PASSED")
    print("Item calculations and subtotal are consistent.")

# STEP 6: Check missing information

review_issues = []

# Get merchant and date
merchant = receipt.get("merchant")
purchase_date = receipt.get("date")

# Check merchant
if not merchant:
    review_issues.append("Merchant name is missing")

else:
    review_issues.append(
        f"Verify merchant name: {merchant}"
    )

# Check purchase date
if not purchase_date:
    review_issues.append("Purchase date is missing")

# Check purchased items
if not items:
    review_issues.append("No purchased items found")


# STEP 7: Display review results

print("\nEXTRACTION REVIEW")
print("-" * 40)

if review_issues:

    print("Status: NEEDS REVIEW")

    for issue in review_issues:
        print("-", issue)

else:
    print("No missing fields detected")


# STEP 8: Create validation report

financial_passed = len(errors) == 0

validation_report = {
    "financial_checks_passed": financial_passed,
    "needs_review": bool(review_issues or errors),
    "financial_errors": errors,
    "review_issues": review_issues
}

# Save validation report
output_file = (
    BASE_DIR / "local_data" / "structured"
    / "validation_report.json"
)

output_file.parent.mkdir(parents=True, exist_ok=True)

output_file.write_text(
    json.dumps(validation_report, indent=2),
    encoding="utf-8"
)

print("\nValidation report saved successfully!")