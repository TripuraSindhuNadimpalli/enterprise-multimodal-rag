import re


def decompose_query(query: str) -> list[str]:
    normalized = query.lower().strip()

    multi_project_patterns = [
        r"what projects",
        r"which projects",
        r"recommended projects",
        r"projects.*internship",
        r"projects.*portfolio",
    ]

    is_multi_project_query = any(
        re.search(pattern, normalized)
        for pattern in multi_project_patterns
    )

    if is_multi_project_query:
        return [
            "What is Project 1?",
            "What is Project 2?",
            "What is Project 3?",
            "What is Project 4?",
        ]

    return [query]