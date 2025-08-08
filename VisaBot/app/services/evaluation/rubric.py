from __future__ import annotations

from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from loguru import logger

from .normalizer import NormalizedFeatures


@dataclass
class ScoreBreakdown:
    ties: int
    travel: int
    financials: int
    age: int
    penalties: int


def _score_ties(feat: NormalizedFeatures) -> Tuple[int, List[str]]:
    score = 0
    strengths: List[str] = []

    # Business/home ties (max 40)
    # Physical premises (20)
    if feat.business_premises is True:
        score += 20
        strengths.append("Physical office/shop/warehouse with employees")

    # Digital presence (10)
    if feat.business_online_presence is True:
        score += 10
        strengths.append("Digital presence (website/Facebook)")

    # Assets/inventory/manufacturing footprint (10)
    if feat.business_assets is True:
        score += 10
        strengths.append("Manufacturing/inventory/agricultural assets")
    else:
        # fallback inference
        inferred_assets = feat.business_premises is True and (feat.business_type or "")
        if inferred_assets:
            score += 10
            strengths.append("Business footprint/inventory inferred from premises and type")

    # If not a business profile, limit ties to at most 10 based on employment (we don't have explicit employment ties here)
    if not feat.is_business:
        score = min(score, 10)

    return score, strengths


def _score_travel(feat: NormalizedFeatures) -> Tuple[int, List[str], List[str]]:
    score = 0
    strengths: List[str] = []
    risks: List[str] = []

    # Travel count (max 15)
    if feat.travel_count >= 3:
        score += 15
        strengths.append("3+ international trips")
    elif feat.travel_count == 2:
        score += 10
        strengths.append("2 international trips")
    elif feat.travel_count == 1:
        score += 5
        strengths.append("1 international trip")
    else:
        risks.append("No previous international travel")

    # Recency (max 10)
    y = feat.years_since_last_travel if feat.years_since_last_travel is not None else 99
    if y <= 2:
        score += 10
        strengths.append("Recent travel within 2 years")
    elif y <= 5:
        score += 7
        strengths.append("Travel within last 3–5 years")
    elif y <= 10:
        score += 3
        strengths.append("Travel 6–10 years ago")
    else:
        # >10 or unknown
        risks.append("Last international travel older than 10 years or unknown")

    # Heavy/Schengen (max 10)
    if feat.has_heavy_visa or feat.has_schengen_travel:
        if y <= 2:
            score += 10
            strengths.append("Top-tier/Schengen visa with recent travel")
        elif y <= 5:
            score += 7
            strengths.append("Top-tier/Schengen visa within 3–5 years")
        elif y <= 10:
            score += 3
            strengths.append("Top-tier/Schengen visa within 6–10 years")
        else:
            score += 1
            strengths.append("Historic top-tier/Schengen visa (>10 years)")

    return score, strengths, risks


def _score_financials(feat: NormalizedFeatures) -> Tuple[int, List[str], List[str]]:
    score = 0
    strengths: List[str] = []
    risks: List[str] = []

    # Closing balance (max 12)
    cb = feat.closing_balance_pk
    if cb >= 2_000_000:
        score += 12
        strengths.append("Closing balance ≥ 2M PKR")
    elif 1_500_000 <= cb < 2_000_000:
        score += 6
        strengths.append("Closing balance 1.5–2M PKR")
        risks.append("Closing balance below 2M PKR threshold")
    elif 1_000_000 <= cb < 1_500_000:
        score += 2
        strengths.append("Closing balance 1–1.5M PKR")
        risks.append("Closing balance below 2M PKR threshold")
    else:
        risks.append("Insufficient or unknown closing balance")

    # Annual income declared (max 8)
    inc = feat.annual_income_pk
    inc_sub = 0
    if inc >= 1_200_000:
        inc_sub = 8
        strengths.append("Annual income ≥ 1.2M PKR (tax-declared)")
    elif 800_000 <= inc < 1_200_000:
        inc_sub = 4
        strengths.append("Annual income 0.8–1.2M PKR (tax-declared)")
        risks.append("Income below 1.2M PKR ideal threshold")
    elif 500_000 <= inc < 800_000:
        inc_sub = 2
        strengths.append("Annual income 0.5–0.8M PKR (tax-declared)")
        risks.append("Income below 1.2M PKR ideal threshold")
    else:
        risks.append("Low or unknown annual income")

    if feat.is_tax_filer is False:
        inc_sub = int(inc_sub * 0.5)
        risks.append("Not a tax filer (reduced credit for income)")
    score += inc_sub

    return score, strengths, risks


def _score_age(feat: NormalizedFeatures) -> Tuple[int, List[str], List[str]]:
    score = 0
    strengths: List[str] = []
    risks: List[str] = []
    age = feat.age if feat.age is not None else -1
    if age > 30:
        score = 5
        strengths.append("Age > 30 (maturity)")
    elif 25 <= age <= 30:
        score = 3
        strengths.append("Age 25–30 (acceptable)")
    elif 0 <= age < 25:
        score = 0
        risks.append("Age < 25 (higher scrutiny)")
    return score, strengths, risks


def _penalties(feat: NormalizedFeatures) -> Tuple[int, List[str]]:
    p = 0
    risks: List[str] = []
    # Previous Schengen rejection
    if feat.previous_schengen_rejection:
        yrs = feat.previous_schengen_rejection_years_ago or 99
        if yrs <= 2:
            p += 20
            risks.append("Schengen rejection in last 2 years")
        elif yrs <= 5:
            p += 15
            risks.append("Schengen rejection 3–5 years ago")
        elif yrs <= 10:
            p += 10
            risks.append("Schengen rejection 6–10 years ago")
        else:
            p += 8
            risks.append("Historic Schengen rejection (>10 years)")
    return p, risks


def _banded_ratio(score: int) -> int:
    if score >= 80:
        return 90
    if score >= 60:
        return 70
    if score >= 40:
        return 50
    return 30


def _apply_caps_and_overrides(success_ratio: int, feat: NormalizedFeatures) -> int:
    # Balance hard cap
    if feat.closing_balance_pk < 2_000_000:
        success_ratio = min(success_ratio, 50)

    # Age caution override
    if (feat.age is not None and feat.age < 25) and (feat.travel_count < 2) and (feat.business_premises is not True):
        success_ratio = min(success_ratio, 40)

    return success_ratio


def _confidence(feat: NormalizedFeatures) -> float:
    conf = 0.8
    missing = 0
    if feat.closing_balance_pk == 0:
        missing += 1
    if feat.annual_income_pk == 0:
        missing += 1
    if feat.travel_count == 0 and (feat.years_since_last_travel is None):
        missing += 1
    if feat.business_premises is None:
        missing += 1
    if feat.is_tax_filer is None:
        missing += 1
    conf -= 0.1 * missing
    return max(0.3, min(0.95, conf))


def _recommendations(feat: NormalizedFeatures) -> List[str]:
    recs: List[str] = []
    # First-time Schengen guidance
    if not feat.has_schengen_travel and not (feat.has_heavy_visa is True):
        recs.append("Apply for a Business visa for your first Schengen attempt; avoid Germany/France/Italy initially; consider Belgium/Netherlands/Norway/Spain.")

    # Travel building
    if feat.travel_count < 2 or (feat.years_since_last_travel or 99) > 5:
        recs.append("Build or refresh travel history (consider Turkey, Malaysia, Singapore, Japan, UAE).")

    # Financial documentation
    if feat.closing_balance_pk < 2_000_000:
        recs.append("Increase closing balance to ≥ 2M PKR to improve approval chances.")
    if feat.annual_income_pk < 1_200_000:
        recs.append("Strengthen declared annual income and ensure tax compliance.")
    if feat.is_tax_filer is False:
        recs.append("File taxes and prepare recent returns.")

    # Business ties
    if feat.business_premises is not True:
        recs.append("Document physical business ties (lease, utility bills, payroll, photos of premises).")
    if feat.business_online_presence is not True:
        recs.append("Establish digital presence (website/social) to validate business existence.")

    # Purpose
    recs.append("Have a verifiable purpose (invitation, event, exhibition) and align itinerary accordingly.")

    # Rejection handling
    if feat.previous_schengen_rejection:
        recs.append("Address previous refusal clearly; provide stronger evidence and coherent travel purpose.")

    # Deduplicate while preserving order
    seen = set()
    unique_recs = []
    for r in recs:
        if r not in seen:
            unique_recs.append(r)
            seen.add(r)
    return unique_recs


def _application_strategy(feat: NormalizedFeatures, success_ratio: int) -> str:
    if success_ratio >= 80:
        return "Proceed with application; ensure complete documentation and clear purpose; book appointment and prepare via our portal."
    if success_ratio >= 60:
        return "Apply with proper preparation; reinforce weaker areas and use a strong business purpose/invitation."
    if success_ratio >= 40:
        return "Consider improving travel history/financials first, or apply only with a solid business invitation and strong ties."
    return "Not recommended at this stage; build travel history and strengthen business/financial ties before applying."


def score_profile(feat: NormalizedFeatures) -> Dict[str, Any]:
    logger.info("Scoring profile using rubric")

    ties, tie_strengths = _score_ties(feat)
    travel, travel_strengths, travel_risks = _score_travel(feat)
    financials, fin_strengths, fin_risks = _score_financials(feat)
    age_score, age_strengths, age_risks = _score_age(feat)
    pen, pen_risks = _penalties(feat)

    base_score = ties + travel + financials + age_score - pen
    base_score = max(0, min(100, base_score))

    success_ratio = _banded_ratio(base_score)
    success_ratio = _apply_caps_and_overrides(success_ratio, feat)

    strengths = tie_strengths + travel_strengths + fin_strengths + age_strengths
    risk_factors = travel_risks + fin_risks + age_risks + pen_risks
    recommendations = _recommendations(feat)
    application_strategy = _application_strategy(feat, success_ratio)

    evaluation = {
        "success_ratio": success_ratio,
        "overall_recommendation": (
            "Strong approval likelihood - Proceed with application" if success_ratio >= 80 else
            "Good approval likelihood - Apply with proper preparation" if success_ratio >= 60 else
            "Moderate approval likelihood - Consider improvements first" if success_ratio >= 40 else
            "Low approval likelihood - Build profile before applying"
        ),
        "confidence_level": (
            "High" if success_ratio >= 80 else "Medium" if success_ratio >= 40 else "Low"
        ),
        "matched_scenario": "Rubric-Based Evaluation",
        "strengths": strengths,
        "risk_factors": risk_factors,
        "recommendations": recommendations,
        "application_strategy": application_strategy,
        "required_documents": [
            "Passport (first and second page)",
            "CNIC (front and back)",
            "FRC or MRC",
            "NTN Registration",
            "Tax Returns (last 2 years)",
            "Bank Statement (3 months)",
            "Bank Maintenance Letter",
            "Business Website/Social Links",
            "Travel Itinerary/Invitations"
        ],
        "confidence": _confidence(feat),
        "should_apply": success_ratio >= 60,
        "next_steps": []  # optional: derive from recommendations/risks if needed
    }

    logger.info({
        "base_score": base_score,
        "breakdown": ScoreBreakdown(ties, travel, financials, age_score, pen),
        "evaluation": evaluation,
    })

    return evaluation


