import re


PROJECT_PATTERN = r"^.*Project\s+\d+\s*[—\-:].*$"

GLOBAL_SECTION_PATTERNS = [
    r"^Why\s+these\s+four\??$",
]

SUBSECTION_PATTERNS = [
    r"^Why\s+this\s+project$",
    r"^Features$",
    r"^Technologies$",
    r"^Skills(?:\s+demonstrated)?$",
    r"^Problem$",
    r"^Resume\s+line$",
    r"^Difficulty:.*$",
]


def normalize_heading(line: str) -> str:
    return " ".join(line.strip().split())


def detect_project_title(line: str) -> str | None:
    cleaned = normalize_heading(line)

    if not cleaned:
        return None

    if re.match(PROJECT_PATTERN, cleaned, flags=re.IGNORECASE):
        return cleaned

    return None


def detect_global_section(line: str) -> str | None:
    cleaned = normalize_heading(line)

    if not cleaned:
        return None

    for pattern in GLOBAL_SECTION_PATTERNS:
        if re.match(pattern, cleaned, flags=re.IGNORECASE):
            return cleaned

    return None


def detect_subsection_title(line: str) -> str | None:
    cleaned = normalize_heading(line)

    if not cleaned:
        return None

    for pattern in SUBSECTION_PATTERNS:
        if re.match(pattern, cleaned, flags=re.IGNORECASE):
            return cleaned

    return None