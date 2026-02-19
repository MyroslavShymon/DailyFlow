from daily_flow.db.repositories.idea_repo import Idea, Sphere


def render_idea(idea: Idea) -> str:
    intent_map = {
        "problem": "🚩 Проблема",
        "solution": "🛠 Рішення",
        "hypothesis": "🧪 Гіпотеза",
        "question": "❓ Питання",
        "insight": "💡 Інсайт",
        "todo": "📝 ToDo",
    }

    intent_display = intent_map.get(str(idea.intent), "—") if idea.intent is not None else "—"

    return (
        f"💡 Ідея\n\n"
        f"🆔 ID: {idea.id}\n"
        f"🏷️ Назва: {idea.title}\n"
        f"🎯 Тип: {intent_display}\n"
        f"📝 Опис: {idea.description or '—'}\n"
        f"🕒 Створено: {idea.created_at}"
    )


def render_sphere(sphere: Sphere) -> str:
    return (
        f"🧭 Сфера\n\n"
        f"🆔 ID: {sphere.id}\n"
        f"🏷️ Назва: {sphere.name}\n"
        f"📝 Опис: {sphere.description or '—'}"
    )
