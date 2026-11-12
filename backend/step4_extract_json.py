from pathlib import Path
from pydantic import BaseModel, Field
from ollama import chat


# 1. Define the structure of a receipt item
class ReceiptItem(BaseModel):
    name: str
    quantity: float | None = None
    unit_price: float | None = None
    line_total: float | None = None


# 2. Define the structure of a receipt
class Receipt(BaseModel):
    merchant: str | None = None
    date: str | None = None
    items: list[ReceiptItem] = Field(default_factory=list)
    subtotal: float | None = None
    tax: float | None = None
    total: float | None = None


# 3. Locate the cleaned OCR text
BASE_DIR = Path(__file__).resolve().parent

input_file = BASE_DIR / "local_data" / "ocr" / "cleaned_receipt.txt"

if not input_file.exists():
    raise FileNotFoundError("Cleaned receipt text not found!")


# 4. Read the receipt text
receipt_text = input_file.read_text(encoding="utf-8")


# 5. Send the receipt text to Ollama
response = chat(
    model="gpt-oss:20b",
    messages=[
        {
            "role": "system",
            "content": (
                "You extract structured information from receipts. "
                "Use only information found in the receipt. "
                "Do not invent missing values. "
                "Use null for unknown fields. "
                "Keep product names and dates as printed. "
                "Do not assume quantity is 1 when it is missing. "
                "Return structured JSON."
            )
        },
        {
            "role": "user",
            "content": receipt_text
        }
    ],
    format=Receipt.model_json_schema(),
    options={"temperature": 0}
)


# 6. Validate the JSON structure
receipt = Receipt.model_validate_json(response.message.content)


# 7. Display the result
print("\nStructured Receipt Data:")
print(receipt.model_dump_json(indent=2))


# 8. Save the JSON locally
output_dir = BASE_DIR / "local_data" / "structured"
output_dir.mkdir(parents=True, exist_ok=True)

output_file = output_dir / "receipt.json"

output_file.write_text(
    receipt.model_dump_json(indent=2),
    encoding="utf-8"
)

print("\nStructured JSON saved successfully!")