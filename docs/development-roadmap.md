# ReceiptIQ — Development Roadmap

**Project owner:** Solo developer  
**Project status:** Phase 0 / planning  
**Build target:** Local-first personal receipt scanner, operated from a phone browser

## Phase 0 — Repository foundation

- [x] Define MVP goals and non-goals.
- [x] Choose initial stack and architecture.
- [x] Create repository structure, README, and architecture documentation.
- [x] Add privacy-minded `.gitignore`.
- [ ] Create an empty GitHub repository and push the initial files.
- [ ] Open GitHub Issues for each implementation milestone.

**Done when:** The repository is online, documentation renders properly, and no personal data is committed.

## Phase 1 — OCR proof of concept

- [ ] Create Python environment on Apple Silicon and pin compatible dependencies.
- [ ] Test PaddleOCR against 5–10 synthetic or permission-cleared receipt photos.
- [ ] Save text + detection metadata in memory or excluded local files.
- [ ] Document common failures (faded ink, skew, clipped edges, small text).

**Done when:** A local script extracts recognizable text from different images and has repeatable tests/fixtures.

## Phase 2 — Structured AI extraction

- [ ] Select and benchmark a suitable local Ollama model.
- [ ] Define Pydantic receipt/line-item schemas with nullable unknown values.
- [ ] Convert OCR text into a structured draft via the model.
- [ ] Enforce parse failures, timeouts, and retry rules without fabricating data.
- [ ] Add regression tests for realistic receipts and awkward layouts.

**Done when:** A local call returns schema-valid JSON drafts for a diverse small test set.

## Phase 3 — Validation and normalization

- [ ] Normalize merchant/date/currency where supported by source evidence.
- [ ] Check line arithmetic and receipt total reconciliation using `Decimal`.
- [ ] Preserve raw values and add review flags for ambiguity/inconsistency.
- [ ] Add receipt duplicate warning, without automatic deletion.
- [ ] Establish extraction quality baseline with labeled test cases.

**Done when:** Incorrect/uncertain receipts are flagged, not silently stored as verified.

## Phase 4 — SQLite persistence and API

- [ ] Design relational schema and migrations.
- [ ] Build FastAPI extraction and confirmed-receipt CRUD endpoints.
- [ ] Validate upload files and sizes; manage temporary data safely.
- [ ] Add API tests for failures and successful confirmed saves.

**Done when:** Confirmed receipt data persists and can be read, edited, and listed locally.

## Phase 5 — Mobile-friendly React interface

- [ ] Scaffold React + Vite with accessible responsive layouts.
- [ ] Implement mobile camera upload and image preview.
- [ ] Display extracted data, review flags, and editable fields.
- [ ] Support confirmation and saving; handle loading/failure states.
- [ ] Test with an actual phone on the same trusted network as the Mac.

**Done when:** You can photograph, review, correct, and save a receipt from your phone.

## Phase 6 — Spending analytics and polish

- [ ] Receipt list, filters, monthly/category spending reports.
- [ ] CSV export and transparent category assignment.
- [ ] Add privacy and local setup documentation.
- [ ] Add demo screenshots using synthetic receipts.
- [ ] Compare extraction approaches and document measured results.

**Done when:** The workflow is useful for recurring personal expense tracking and demonstrable as a portfolio project.

## Optional later additions

- Product price history after robust product/unit matching.
- Auto-crop, orientation correction, and multiple photo stitching.
- Local network authentication, encrypted backups, multi-device access.
- PDF receipts and email import (with explicit consent).

## Suggested first issues

1. `setup: establish backend environment on Apple Silicon`
2. `ocr: PaddleOCR baseline extraction script`
3. `schemas: define receipt and line-item contracts`
4. `ai: local Ollama receipt parser`
5. `validation: decimal arithmetic and review flags`
6. `api: create extraction endpoint`
7. `frontend: mobile camera upload and review screen`
8. `analytics: monthly category totals`

## Git workflow

Use a feature branch per milestone, open a pull request, and keep commits small. Example messages:

- `docs: add initial architecture and roadmap`
- `feat(ocr): extract receipt text from uploaded image`
- `test(validation): cover discounts and subtotal mismatch`
