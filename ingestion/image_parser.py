from io import BytesIO

import pytesseract
from PIL import Image


def extract_text_from_image(file_bytes: bytes) -> list[dict]:
    image = Image.open(BytesIO(file_bytes))

    image = image.convert("RGB")

    text = pytesseract.image_to_string(image).strip()

    if not text:
        return []

    return [
        {
            "page_number": 1,
            "text": text,
        }
    ]