from ingestion.chunker import chunk_text
from ingestion.section_detector import (
    detect_project_title,
    detect_subsection_title,
    detect_global_section,
)


def create_structured_chunks(
    text: str,
    current_parent_section: str | None = None,
    current_subsection: str | None = None,
) -> tuple[list[dict], str | None, str | None]:

    lines = text.splitlines()

    structured_chunks = []

    parent_section = current_parent_section
    subsection = current_subsection
    current_lines = []

    def flush_current_text():
        nonlocal current_lines

        section_text = "\n".join(current_lines).strip()

        if not section_text:
            current_lines = []
            return

        chunks = chunk_text(section_text)

        for chunk in chunks:
            structured_chunks.append(
                {
                    "parent_section_title": parent_section,
                    "section_title": subsection,
                    "chunk_type": "content",
                    "text": chunk,
                }
            )

        current_lines = []

    for line in lines:

        # Check for a global section first
        global_section = detect_global_section(line)

        if global_section:
            flush_current_text()

            parent_section = None
            subsection = global_section
            continue

        # Check for a project title
        project_title = detect_project_title(line)

        if project_title:
            flush_current_text()

            parent_section = project_title
            subsection = None
            continue

        # Check for subsection title
        subsection_title = detect_subsection_title(line)

        if subsection_title:
            flush_current_text()

            subsection = subsection_title
            continue

        # Normal content
        current_lines.append(line)

    # Flush remaining text
    flush_current_text()

    return (
        structured_chunks,
        parent_section,
        subsection,
    )