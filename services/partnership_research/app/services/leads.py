def score_lead(lead: dict[str, str]) -> dict[str, object]:
    text = " ".join(filter(None, [lead.get("title"), lead.get("description")])).lower()
    score = 0.0

    for keyword in ("nutrition", "food", "healthy", "fitness", "lifestyle"):
        if keyword in text:
            score += 1.0

    return {
        "score": score,
        "summary": "Initial heuristic score. Replace with richer enrichment later.",
    }
