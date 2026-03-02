from datetime import date, datetime


def parse_to_date(text: str) -> date | None:
    try:
        valid_date = datetime.strptime(text, "%d-%m-%Y").date()
        return valid_date
    except ValueError:
        return
