import re


def clean_extracted_text(text: str) -> str:
    if not text:
        return ""

    # Remove URLs
    text = re.sub(r"https?://\S+", "", text)

    # Remove common PDF date/time footer patterns
    text = re.sub(
        r"\d{1,2}/\d{1,2}/\d{2,4},?\s+\d{1,2}:\d{2}\s*(AM|PM)?",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Remove page-counter patterns such as 51/59
    text = re.sub(r"\b\d+\s*/\s*\d+\b", "", text)

    # Remove repeated spaces while preserving line structure
    text = re.sub(r"[ \t]+", " ", text)

    # Reduce excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()