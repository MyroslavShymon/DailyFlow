from daily_flow.db.repositories.activity.activity_repo import Activity
from daily_flow.db.repositories.activity.activity_usage_repo import ActivityUsage
from daily_flow.db.repositories.activity.category_repo import Category


def _truncate(text: str | None, max_len: int = 220) -> str:
    if not text:
        return "—"
    text = str(text).strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def render_activity(a: Activity) -> str:
    prep = "✅ так" if a.requires_preparation else "❌ ні"

    return (
        "🎯 **Активність**\n\n"
        f"🆔 ID: `{a.id}`\n"
        f"🏷️ **{a.title}**\n"
        f"📝 {_truncate(a.description, 600) or '—'}\n\n"
        f"👥 Соціально: {a.social_type or '—'}\n"
        f"   • Людей: {a.people_count_min or '—'} – {a.people_count_max or '—'}\n"
        f"   • З ким: {_truncate(a.specific_with) or '—'}\n\n"
        f"🕒 Час: {a.time_context or '—'} | {a.time_of_day or '—'}\n"
        f"   • Тривалість: {a.duration_min_minutes or '—'} – {a.duration_max_minutes or '—'} хв\n\n"
        f"⚡ Енергія:\n"
        f"   • Потрібно: {a.energy_required_min or '—'} – {a.energy_required_max or '—'}\n"
        f"   • Ефект(чи виснажує): {a.energy_gain or '—'}\n"
        f"🙂 В якому стані я можу бути: {a.mood_min or '—'} – {a.mood_max or '—'}\n\n"
        f"💸 Вартість: {a.cost_level or '—'}\n"
        f"📍 Локація: {a.location_type or '—'}\n"
        f"🧰 Підготовка: {prep}\n"
        f"   • {_truncate(a.preparation_notes) or '—'}"
    )


def render_activity_compact(a: Activity) -> str:
    return f"• `{a.id}` — **{_truncate(a.title, 80)}**"


def render_category(c: Category) -> str:
    return (
        "🏷️ **Категорія**\n\n"
        f"🆔 ID: `{c.id}`\n"
        f"🏷️ Назва: **{c.name}**\n"
        f"📝 Опис: {_truncate(c.description, 600)}"
    )


def render_category_compact(c: Category) -> str:
    return f"• `{c.id}` — **{_truncate(c.name, 80)}**"


def render_activity_usage(u: ActivityUsage) -> str:
    return (
        "📌 **Виконання активності**\n\n"
        f"🆔 Usage ID: `{u.id}`\n"
        f"🎯 Activity ID: `{u.activity_id}`\n"
        f"🕒 Коли: **{u.used_at}**\n"
        f"⏱️ Тривалість: "
        f"{u.duration_actual_minutes if u.duration_actual_minutes is not None else '—'} хв\n\n"
        f"⭐ Оцінка: {u.rating_before or '—'} → {u.rating_after or '—'}\n"
        f"🙂 Стан: {u.mood_before or '—'} → {u.mood_after or '—'}\n"
        f"⚡ Енергія: {u.energy_before or '—'} → {u.energy_after or '—'}\n\n"
        f"📝 Нотатки: {_truncate(u.notes, 700)}"
    )


def render_assign_category_result(is_inserted: bool, values: dict) -> str:
    activity_id = values.get("activity_id", "—")
    category_id = values.get("category_id", "—")

    if is_inserted:
        return (
            "✅ **Категорію привʼязано**\n\n"
            f"🎯 Activity ID: `{activity_id}`\n"
            f"🏷️ Category ID: `{category_id}`"
        )
    return (
        "ℹ️ **Звʼязок вже існує**\n\n"
        f"🎯 Activity ID: `{activity_id}`\n"
        f"🏷️ Category ID: `{category_id}`"
    )
