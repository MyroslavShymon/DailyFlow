from daily_flow.db.repositories.mood_log_repo import MoodLog


def render_mood_log(mood_log: MoodLog) -> str:
    return f"""📅 {mood_log.day or "—"}

🙂 Радість: {mood_log.joy or "—"}
✨ Інтерес: {mood_log.interest or "—"}
🧘 Спокій: {mood_log.calm or "—"}

⚡ Енергія: {mood_log.energy or "—"}
😰 Тривога: {mood_log.anxiety or "—"}
😢 Смуток: {mood_log.sadness or "—"}
😤 Роздратування: {mood_log.irritation or "—"}
🥱 Втома: {mood_log.fatigue or "—"}
😱 Страх: {mood_log.fear or "—"}
💪 Впевненість: {mood_log.confidence or "—"}
😴 Сон: {mood_log.sleep or "—"}
"""
