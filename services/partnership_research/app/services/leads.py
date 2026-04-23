from __future__ import annotations

from typing import Any


NICHE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "pp_nutrition": ("пп", "правильное питание", "рецепт", "рецепты", "nutrition", "meal", "food"),
    "weight_loss": ("похудение", "худеем", "снижение веса", "weight loss", "fat loss", "calorie", "калории"),
    "wellness": ("зож", "healthy", "wellness", "lifestyle", "здоровье"),
    "fitness": ("фитнес", "тренер", "trainer", "workout", "fitness"),
    "nutritionist": ("нутрициолог", "nutritionist", "diet", "dietitian"),
}

CONTACT_KEYWORDS = (
    "реклама",
    "сотрудничество",
    "партнерство",
    "партнёрство",
    "по рекламе",
    "для связи",
    "связь",
    "ads",
    "advertising",
    "collab",
    "partnership",
    "contact",
    "@",
)


def _normalized_text(parts: list[str | None]) -> str:
    return " ".join(part.strip().lower() for part in parts if part and part.strip())


def _infer_niche(text: str) -> str:
    scores: dict[str, int] = {}
    for niche, keywords in NICHE_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in text)
        if score > 0:
            scores[niche] = score
    if not scores:
        return "other"
    return max(scores.items(), key=lambda item: item[1])[0]


def score_lead(lead: dict[str, Any]) -> dict[str, object]:
    text = _normalized_text(
        [
            str(lead.get("title") or ""),
            str(lead.get("description") or ""),
            str(lead.get("recent_text") or ""),
        ]
    )
    member_count = int(lead.get("member_count") or 0)
    recent_posts = int(lead.get("recent_posts_count") or 0)
    niche = _infer_niche(text)

    score = 0.0
    reasons: list[str] = []

    if niche != "other":
        score += 3.0
        reasons.append(f"релевантная ниша: {niche}")

    if 200 <= member_count <= 10_000:
        score += 3.0
        reasons.append("аудитория подходит для barter/test first")
    elif 100 <= member_count < 200:
        score += 1.5
        reasons.append("аудитория маленькая, но уже пригодна для точечного теста")
    elif 30 <= member_count < 100:
        score += 0.5
        reasons.append("аудитория очень маленькая, нужен ручной отбор")
    elif 0 < member_count < 30:
        score -= 2.0
        reasons.append("аудитория слишком маленькая для приоритетного outreach")
    elif 10_000 < member_count <= 50_000:
        score += 1.5
        reasons.append("аудитория средняя, можно смотреть после малого сегмента")
    elif member_count > 50_000:
        score -= 1.0
        reasons.append("аудитория крупная, скорее на потом")

    if recent_posts >= 5:
        score += 2.0
        reasons.append("есть недавняя активность")
    elif recent_posts >= 1:
        score += 1.0
        reasons.append("есть хоть какая-то недавняя активность")

    if any(keyword in text for keyword in CONTACT_KEYWORDS):
        score += 2.0
        reasons.append("видны сигналы для связи или рекламы")

    if "звезд" in text or "звёзд" in text or "celebrity" in text:
        score -= 1.5
        reasons.append("похоже на слишком крупный или медийный канал")

    if member_count == 0:
        reasons.append("размер аудитории не удалось подтвердить")

    if niche != "other" and score >= 7:
        recommendation = "high_priority"
    elif score >= 4:
        recommendation = "review"
    else:
        recommendation = "low_priority"

    return {
        "score": round(score, 2),
        "niche": niche,
        "recommendation": recommendation,
        "summary": "; ".join(reasons) if reasons else "Сигналов пока мало, нужен ручной просмотр.",
    }
