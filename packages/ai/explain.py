"""Explainability layer — generates human-readable explanations for graph paths, rankings, and recommendations.

No LLM calls. Pure deterministic reasoning from graph data."""


def explain_path(path: list[dict]) -> str:
    if not path:
        return "No connection found."

    parts = []
    for hop in path:
        frm = hop.get("from", {})
        to = hop.get("to", {})
        via = hop.get("via", "connected")
        frm_name = frm.get("name", "?")
        to_name = to.get("name", "?")
        parts.append(f"{frm_name} --[{via}]--> {to_name}")

    return " → ".join(parts)


def explain_rank_score(person_name: str, score: float, factors: dict) -> str:
    lines = [f"**{person_name}** — Score: {score:.0f}/100"]
    weights = {
        "hiring_influence": ("Hiring influence", 25),
        "technical_similarity": ("Technical similarity", 25),
        "shared_technologies": ("Shared technologies", 20),
        "team_relevance": ("Team relevance", 15),
        "public_activity": ("Public activity", 15),
    }
    for key, (label, max_score) in weights.items():
        val = factors.get(key, 0)
        bar = "█" * int(val / 5) + "░" * (5 - int(val / 5))
        lines.append(f"  {label}: {bar} {val:.0f}/{max_score}")

    return "\n".join(lines)


def explain_skill_match(matches: list[dict]) -> list[str]:
    satisfied = []
    partial = []
    missing = []
    for m in matches:
        status = m.get("status", "")
        skill = m.get("skill", "")
        if status == "satisfied":
            satisfied.append(f"✅ {skill}")
        elif status == "partial":
            partial.append(f"⚠️ {skill} (partial)")
        else:
            missing.append(f"❌ {skill}")
    return satisfied + partial + missing


def explain_recommendation(person_name: str, strengths: list[str], shared_interests: list[str]) -> str:
    parts = [f"**Why {person_name}?**"]
    if strengths:
        parts.append("  Strengths: " + ", ".join(strengths[:3]))
    if shared_interests:
        parts.append("  Shared: " + ", ".join(shared_interests[:3]))
    return "\n".join(parts)


def explain_follow_up(person_name: str, days_since_last: int, last_action: str | None) -> str:
    if days_since_last <= 1:
        return f"Too soon to follow up with {person_name} — you just reached out."
    if days_since_last <= 3:
        return f"Wait a few more days before following up with {person_name}."
    if days_since_last <= 7:
        return f"Good time to follow up with {person_name} — it's been {days_since_last} days."
    if days_since_last <= 14:
        return f"**Follow up with {person_name}** — it's been {days_since_last} days since {last_action or 'last contact'}."
    return f"**High priority: Follow up with {person_name}** — it's been {days_since_last} days. Don't let this go cold."
