from enum import StrEnum


class CommonMoodLogValidationErrors(StrEnum):
    MISSING_DAY="missing_day"
    DAY_DUPLICATE="day_duplicate"
    MOOD_IS_OUT_OF_RANGE="mood_is_out_of_range_1_7"
    MISSING_REQUIRED_COLUMNS="missing_required_columns"
    MOOD_IS_ONLY_INT="mood_is_only_int_value"

class CommonMoodLogValidationWarnings(StrEnum):
    NO_OPTIONAL_FIELDS="no_optional_fields"
