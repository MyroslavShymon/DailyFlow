MART_QUERY = """
SELECT
    COALESCE(mood_log.day, cml.day) AS day,
    cml.mood AS common_mood_log,
    cml.note AS note,
    joy, interest, calm, energy, anxiety, 
    sadness, irritation, fatigue, fear, 
    confidence, sleep
FROM main.mood_log
FULL OUTER JOIN main.common_mood_log cml ON main.mood_log.day = cml.day;
"""
