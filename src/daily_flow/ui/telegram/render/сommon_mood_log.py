from daily_flow.db.repositories.common_mood_repo import CommonMoodLog


def render_common_mood_log(common_mood_log: CommonMoodLog) -> str:
    mood_emoji = {
        1: "😢 жахливо",
        2: "☹️ погано",
        3: "😐 посередньо",
        4: "🙂 непогано",
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


# def render_tag_impact(dto: UpsertTagImpactDTO) -> str:
#     # Мапінг впливу на зрозумілі символи
#     impact_map = {
#         -1: "🔻 Негативно впливає",
#          0: "🟡 Нейтрально",
#          1: "☘️ Позитивно впливає"
#     }
#
#     impact_display = impact_map.get(dto.impact, "Невідомо")
#
#     return (
#         f"🏷️ **Вплив події (тег)**\n"
#         f"---"
#         f"📅 Дата: **{dto.day}**\n"
#         f"🔖 Тег: `#{dto.tag}`\n"
#         f"⚡ Ефект: **{impact_display}**"
#     )