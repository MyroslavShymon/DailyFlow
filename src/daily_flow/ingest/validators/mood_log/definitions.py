from enum import StrEnum


class MoodLogValidationErrors(StrEnum):
    MISSING_DAY="missing_day"
    DAY_DUPLICATE="day_duplicate"
    NO_MOODS_VALUES="no_moods_values"
    MOOD_IS_OUT_OF_RANGE="mood_is_out_of_range_1_4"
    MISSING_REQUIRED_COLUMNS="missing_required_columns"
    MOOD_IS_ONLY_INT="mood_is_only_int_value"

class MoodLogValidationWarnings(StrEnum):
    SLEEP_ONLY_VALUE="sleep_only_value"
    MANY_NAN_MOOD_VALUES="many_nan_mood_values"