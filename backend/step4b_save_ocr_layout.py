import json
from pathlib import Path
from paddleocr import PaddleOCR

# 1. Locate the receipt image
BASE_DIR = Path(__file__).resolve().parent

receipt_path = BASE_DIR / "local_data" / "receipts" / "test_receipt_converted.jpg"

if not receipt_path.exists():
    raise FileNotFoundError("Receipt image not found!")


# 2. Initialize PaddleOCR
ocr = PaddleOCR(
    lang="en",
    device="cpu",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False
)


# 3. Run OCR
results = ocr.predict(str(receipt_path))


# 4. Extract text, confidence, and positions
ocr_data = []

for result in results:

    texts = result["rec_texts"]
    scores = result["rec_scores"]
    boxes = result["rec_boxes"]

    for text, score, box in zip(texts, scores, boxes):

        x1, y1, x2, y2 = map(int, box)

        ocr_data.append({
            "text": text,
            "confidence": round(float(score), 3),
            "box": [x1, y1, x2, y2]
        })


# 5. Save results as JSON
output_dir = BASE_DIR / "local_data" / "ocr"
output_dir.mkdir(parents=True, exist_ok=True)

output_file = output_dir / "receipt_layout.json"

output_file.write_text(
    json.dumps(ocr_data, indent=2),
    encoding="utf-8"
)

print("OCR layout saved successfully!")
print("Total detected text regions:", len(ocr_data))
