from __future__ import annotations

from typing import Dict, Any, Optional, List


def build_narrative(evaluation: Dict[str, Any], answers: Dict[str, Any], target_country: Optional[str]) -> str:
    country = answers.get("selected_country") or answers.get("country") or target_country

    success_ratio = evaluation.get("success_ratio")
    # Confidence label intentionally not displayed per formatting request

    # Extract contextual facts
    profession = str(answers.get("profession", "")).strip()
    business_type = str(answers.get("business_type", "")).strip()
    annual_income = answers.get("annual_income")
    closing_balance = answers.get("closing_balance")

    # Travel
    travel = answers.get("travel_history")
    if isinstance(travel, list):
        travel_countries = ", ".join([str(c) for c in travel[:6]])
        has_travel = len(travel) > 0
    elif isinstance(travel, str) and travel.strip():
        travel_countries = travel
        has_travel = True
    else:
        travel_countries = ""
        has_travel = False

    last_year = answers.get("last_travel_year")

    # Build content
    # Intro
    intro = (
        f"Thanks for sharing your details. Based on your information, here’s our assessment"
        + (f" for {country}." if country else ":")
    )

    # Success Ratio line (confidence removed as requested)
    ratio_line = f"**Success Ratio:** {success_ratio}%" if success_ratio is not None else ""

    # 1) Visa type/purpose guidance (use overall recommendation as cue)
    overall = evaluation.get("overall_recommendation", "")
    rec_primary = overall

    # 2) Travel perspective (simple surface)
    if has_travel:
        travel_line = (
            f"You have a reasonable travel history (e.g., {travel_countries})"
            + (f" and your last trip was in {last_year}." if last_year else ".")
        )
    else:
        travel_line = (
            "You don’t appear to have international travel history yet; that can reduce early approval odds unless other areas are strong."
        )

    # 3) Purpose guidance
    purpose_line = (
        "Have a clear and verifiable purpose (event, exhibition, client meetings, or a formal business invitation)."
    )

    # 4) Documentation/ties line
    ties_parts: List[str] = []
    if profession:
        ties_parts.append(f"Profile: {profession}" + (f" ({business_type})." if business_type else "."))
    if annual_income:
        try:
            income_num = int(str(annual_income).split()[0])
            ties_parts.append(f"Tax-declared income ~ {income_num} PKR.")
        except Exception:
            ties_parts.append(f"Declared income: {annual_income}.")
    if isinstance(closing_balance, (int, float)) and closing_balance:
        ties_parts.append(f"Bank balance around {int(closing_balance):,} PKR.")
    elif closing_balance is True:
        ties_parts.append("You can maintain the required closing balance.")
    ties_line = (
        "On documentation, show strong ties with your homeland to ensure visa success. "
        + " ".join(ties_parts)
    ).strip()

    # Scenario/rubric recommendations (bulleted list)
    scenario_recs = evaluation.get("recommendations", []) or []
    recs = [f"- {r}" for r in scenario_recs[:4]]

    # Strategy
    strategy = evaluation.get("application_strategy")

    # Assemble with Markdown-friendly formatting
    parts: List[str] = []
    parts.append(intro)
    if ratio_line:
        parts.append(ratio_line)

    # Recommendations section
    parts.append("\n**Recommendations**")
    parts.append(f"1. {rec_primary}")
    parts.append(f"2. {travel_line}")
    parts.append(f"3. {purpose_line}")
    parts.append(f"4. {ties_line}")

    # Additional tips section
    if recs:
        parts.append("\n**Additionally, keep in mind:**")
        parts.extend(recs)

    # Application strategy (optional, kept at the end)
    if strategy:
        parts.append("\n**Application Strategy**")
        parts.append(strategy)

    parts.append(
        "\nThese are our recommendations. You can now generate a tailored checklist or discuss with our AI Consultant for file preparation."
    )

    return "\n".join(parts)


