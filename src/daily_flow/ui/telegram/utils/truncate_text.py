def truncate_text(text: str, limit: int = 3500) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n…"