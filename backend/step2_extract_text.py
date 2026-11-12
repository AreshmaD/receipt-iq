from pathlib import Path
from paddleocr import PaddleOCR

# Step-1 Find the receipt image
BASE_DIR = Path(__file__).resolve().parent

receipt_path = BASE_DIR/ "local_data"/ "receipts" / "test_receipt_converted.jpg"

# Step-2 Check if the image exists
if not receipt_path.exists():
    raise FileNotFoundError("Receipt image not found!")

# Step-3  Initialize  PaddleOCR
ocr = PaddleOCR(
    lang="en",
    device="cpu",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False
)

# Step-4 Extract text from the receipt
results = ocr.predict(str(receipt_path))

# Step-5 Display extracted text
print("\nExtracted Receipt Text:")
print("--------------------------")

for result in results:
    for text in result["rec_texts"]:
        print(text)

# Save extracted text for later processing
ocr_lines = []

for result in results:
    for text in result["rec_texts"]:
        ocr_lines.append(text)

# Create output folder
output_dir = BASE_DIR/ "local_data"/ "ocr"
output_dir.mkdir(parents=True, exist_ok=True)

# Save extracted text
output_file = output_dir / "raw_receipt.txt"

output_file.write_text(
    "\n".join(ocr_lines),
    encoding="utf-8"
)

print("OCR text saved successfully")