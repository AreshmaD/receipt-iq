# ReceiptIQ — Architecture Design

**Status:** Proposed design; not yet implemented.

## Design goals

- Prioritize extraction accuracy, privacy, and editability over autonomous AI complexity.
- Keep purchase amounts, dates, and source evidence traceable.
- Separate probabilistic recognition (OCR/LLM) from deterministic validation and saving.
- Avoid cloud dependencies in the initial version.

## Data flow

1. Phone browser sends an image (JPEG/PNG; later PDF) to FastAPI.
2. Backend validates content type and size, creates a temporary local job, and preprocesses the image.
3. PaddleOCR returns recognized text and, where available, text positions/confidence.
4. A locally running LLM (via Ollama) parses OCR text into a Pydantic-constrained receipt draft; uncertain fields remain `null`.
5. Python normalizes dates/currency and checks financial consistency with `Decimal`.
6. The API returns a **draft** with flags and provenance for the UI to show.
7. User reviews and edits before explicitly confirming the receipt.
8. FastAPI persists a confirmed receipt and line items in SQLite.
9. Dashboard reads saved data through deterministic API endpoints.

## Core components

| Component | Owns | Does not own |
| --- | --- | --- |
| React client | Capture/upload, review UI, history, charts | OCR, LLM inference, database writes directly |
| FastAPI | Input checks, pipeline coordination, persistence APIs | LLM-based arithmetic |
| PaddleOCR | Text and layout evidence | Determining true accounting totals |
| Ollama LLM | Semantic parsing, label/category suggestions | Final validation or silently correcting prices |
| Validation service | Data schema, totals, mismatches, alerts | Guessing missing values |
| SQLite repositories | CRUD for confirmed receipts/items | Interpreting receipt images |

## Proposed entities

**Receipt:** `id`, `merchant_raw`, `merchant_normalized`, `purchase_date`, `currency`, `subtotal`, `discount_total`, `tax`, `tip`, `fees`, `total`, `status`, `created_at`, `updated_at`.

**LineItem:** `id`, `receipt_id`, `description_raw`, `description_normalized`, `quantity`, `unit_price`, `line_total`, `discount`, `category`, `confidence`.

**ExtractionRun:** `id`, `receipt_id` (nullable until confirmed), `engine_version`, `model`, `raw_ocr_text`, `validation_flags`, `created_at`.

Money is represented as `Decimal` in Python; database storage strategy should avoid binary float rounding (e.g., exact minor units as integer or strings with defined precision).

## Proposed API (not yet implemented)

| Method | Route | Purpose |
| --- | --- | --- |
| `POST` | `/api/receipts/extract` | Upload receipt and return draft + flags |
| `POST` | `/api/receipts` | Confirm and save corrected receipt |
| `GET` | `/api/receipts` | List saved receipts |
| `GET` | `/api/receipts/{id}` | Inspect one saved receipt |
| `PATCH` | `/api/receipts/{id}` | Edit saved fields/items |
| `GET` | `/api/analytics/spending` | Return totals by month/category/merchant |

## Example output contract (illustrative, not extracted)

```json
{
  "merchant": "Example Grocery",
  "purchase_date": "2026-11-12",
  "currency": "USD",
  "items": [
    {
      "description_raw": "MLK 2%",
      "description_normalized": "2% Milk",
      "quantity": "1",
      "unit_price": "3.49",
      "line_total": "3.49",
      "category": "Groceries"
    }
  ],
  "subtotal": "3.49",
  "discount_total": "0.00",
  "tax": "0.00",
  "total": "3.49",
  "validation_status": "needs_review",
  "validation_flags": ["Human confirmation required before saving"]
}
```

## Validation principles

- Check line math when both quantity, price, and line total are known.
- Check that subtotal plus taxes/fees/tips minus discounts matches total **only when the relevant fields are known**.
- Permit legitimate retailer-specific rounding, coupons, deposits, and exemptions; flag rather than overwrite mismatches.
- Distinguish fields that were printed on the receipt from inferred normalized categories.
- Keep unrecognized information `null`; no fabricated products or amounts.
- Flag duplicate receipts by a conservative composite fingerprint; do not auto-delete.

## Phone access and local privacy

The React mobile web app calls the FastAPI server hosted on the Mac. On a home network, bind the development server only as needed and protect access; do not expose `0.0.0.0` outside a trusted LAN. A basic `input type=file accept=image/* capture=environment` can prompt camera capture on supported phones; browser behavior varies. A direct `getUserMedia` preview generally requires HTTPS (except localhost) and camera permission. The phone cannot use the Mac's `localhost` address.

Stored receipt data must remain in local directories excluded from Git. If multi-device access or cloud hosting is added, revisit authentication, encryption, retention, backups, and network controls.

## Evaluation plan

Build a small permission-cleared/synthetic labeled set across different merchants, lighting, and receipt formats. Track:

- Merchant/date/total field exact-match rates.
- Line-item precision and recall.
- Numeric error rates for quantities and prices.
- Percentage of receipts flagged for human review.
- Time per receipt, measured on the local Mac.

Compare OCR + LLM against an image-capable model only after establishing a repeatable baseline. Never claim accuracy without measured tests.
