from datetime import datetime


def parse_to_datetime(text: str) -> datetime | None:
    raw = (text or "").strip()
    if not raw:
        return None

    for fmt in ("%d-%m-%Y %H:%M", "%d-%m-%Y"):
        try:
            parsed = datetime.strptime(raw, fmt)
            return parsed
        except ValueError:
            continue

    return None
