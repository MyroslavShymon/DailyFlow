from sqlalchemy.exc import IntegrityError

class RepoError(Exception):
    """Base error for repository layer."""

class DuplicateDayError(RepoError):
    """UNIQUE(day) violated (record already exists for that day)."""

class DuplicateError(RepoError):
    """UNIQUE() violated (record already exists)."""

class InvalidScoreError(RepoError):
    """CHECK constraint violated (score out of allowed range)."""

# class InvalidFormatError(RepoError):
#     """CHECK constraint violated (invalid format error)."""

class ForeignKeyViolationError(RepoError):
    """Foreign key constraint violated."""

class DBIntegrityError(RepoError):
    """Other integrity error (fallback)."""

class UnknownFieldError(RepoError):
    """Error with unknown fields"""

class MissingRequiredFieldError(RepoError):
    """Error point missing required field"""

class EmptyUpsertPayloadError(RepoError):
    """No payload error"""

class ParentNotFoundError(RepoError):
    """Parent entity is not found"""

def map_integrity_error(e: IntegrityError, table: str | None = None) -> RepoError:
    msg = str(getattr(e, "orig", e)).lower()

    if "unique constraint failed" in msg:
        if table and f"{table}.day" in msg:
            if table == 'mood_log':
                return DuplicateDayError("Mood log for this day already exists")
            if table == 'common_mood_log':
                return DuplicateDayError("Common mood log for this day already exists")
            return DuplicateDayError(f"{table} entry for this day already exists")
        return DuplicateError("Duplicate for this entry")


    if "check constraint failed" in msg:
        # if "1-4" in msg:
        #     return InvalidScoreError("Score out of allowed range, it must be between 1 - 4")
        # if "1-7" in msg:
        #     return InvalidScoreError("Score out of allowed range, it must be between 1 - 7")
        return InvalidScoreError("Out of allowed range")

    if "foreign key constraint failed" in msg:
        return ForeignKeyViolationError("Related entity not found (FK violation)")

    return DBIntegrityError("Integrity error")
