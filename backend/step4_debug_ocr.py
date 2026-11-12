from pathlib import Path

# Find backend folder
BASE_DIR = Path(__file__).resolve().parent

# Locate OCR output
ocr_file = BASE_DIR / "local_data" / "ocr" / "cleaned_receipt.txt"

# Read extracted text
receipt_text = ocr_file.read_text(encoding="utf-8")

# Split text into separate lines
lines = receipt_text.splitlines()

print("\nOCR OUTPUT ANALYSIS")
print("--------------------")

# Display each line with its position
for index, line in enumerate(lines, start=1):
    print(f"{index}: {line}")

print("--------------------")
print("Total OCR lines:", len(lines))