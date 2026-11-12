from PIL import Image
from pathlib import Path

# Step1 Location of receipt image
receipt_path = Path("local_data/receipts/test_receipt_converted.jpg")

#Step2 Check whether the image exists
if not receipt_path.exists():
    print("Receipt image not found!")

else:
    # Open and inspect the image
    with Image.open(receipt_path) as image:
        print("Receipt loaded succesfully!")
        print("Image Size:", image.size)
        print("Image Format:", image.format)