from daily_flow.db.repositories.common_mood_repo import CommonMoodLog, MoodTagImpact


def render_common_mood_log(common_mood_log: CommonMoodLog) -> str:
    mood_emoji = {
        1: "😢 жахливо",
        2: "☹️ погано",
        3: "😐 посередньо",
        4: "🙂 нормально",
        5: "😊 добре",
        6: "😁 чудово",
        7: "🤩 неймовірно"
    }

    mood_display = mood_emoji.get(common_mood_log.mood, "—")

    return (
        f"✨ Загальний стан дня\n\n"
        f"📅 Дата: {common_mood_log.day}\n"
        f"🌈 Настрій: {mood_display} ({common_mood_log.mood if common_mood_log.mood else '—'}/7)\n"
        f"📝 Нотатка: {common_mood_log.note or 'відсутня'}"
    )


def render_tag_impact(tag_impact: MoodTagImpact, day: str) -> str:
    impact_map = {
        -1: "🔻 Негативно впливає",
         0: "🟡 Нейтрально",
         1: "☘️ Позитивно впливає"
    }

    impact_display = impact_map.get(tag_impact.impact, "Невідомо")

    return (
        f"🏷️ **Вплив події (тег)**\n"
        f"---"
        f"📅 Дата: **{day}**\n"
        f"🔖 Тег: `#{tag_impact.tag}`\n"
        f"⚡ Ефект: **{impact_display}**"
    )