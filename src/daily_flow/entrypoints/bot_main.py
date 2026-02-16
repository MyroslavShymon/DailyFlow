import logging
from datetime import date

from daily_flow.app.container import build_container
from daily_flow.config.db import load_db_settings
from daily_flow.services.errors import ServiceError
from daily_flow.services.mood_log.dto import UpsertMoodLogDTO

logger = logging.getLogger(__name__)

def main() -> None:
    settings = load_db_settings()
    c = build_container(settings)

    try:
        dto = UpsertMoodLogDTO(
            day=date(2000, 1, 1),
            joy=3,
            interest=3,
            calm=3,
            energy=3,
            anxiety=3,
            sadness=3,
            irritation=3,
            fatigue=3,
            fear=3,
            confidence=3,
            sleep=3,
        )
        # saved = c.mood_log_service.upsert_mood_log(dto)
        # print("SAVED:", saved)
        #
        # got = c.mood_log_service.get_mood_log_by_day(date(2000, 1, 2))
        # print("GOT:", got)

        rng = c.mood_log_service.get_list_by_date_range(date(1999, 1, 2), date(2027, 1, 2))
        print("RANGE:", rng)

        # deleted = c.mood_log_service.delete_mood_log_by_day(dto.day)
        # print("DELETED:", deleted)
    except ServiceError as e:
        logger.error("Service error: %s", e)


if __name__ == "__main__":
    main()