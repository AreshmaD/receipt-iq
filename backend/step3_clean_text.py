from pathlib import Path

# Step1 - Find the backen folder
BASE_DIR = Path(__file__).resolve().parent

# Step2 - Locate Saved OCR text
input_file = BASE_DIR/ "local_data"/ "ocr" / "raw_receipt.txt"

# Step3 - Read extracted text
raw_text = input_file.read_text(encoding="utf-8")

# Step4 - Clean each line
cleaned_lines = []

for line in raw_text.splitlines():

    # Remove unnecessary spaces
    clean_line = " ".join(line.split())

    # Skip empty lines
    if clean_line:
        cleaned_lines.append(clean_line)

# Step5 - Combine cleaned lines
cleaned_text = "\n".join(cleaned_lines)

# Step6 - Display cleaned text
print("\nCleaned Receipt Text:")
print("-----------------------")
print(cleaned_text)

# Step7 - Save cleaned text
output_file = BASE_DIR /"local_data" / "ocr" /"cleaned_receipt.txt"

output_file.write_text(cleaned_text, encoding="utf-8")

print("\nClenaed text saved succesfully!")