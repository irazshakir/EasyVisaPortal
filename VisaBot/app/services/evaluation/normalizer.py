from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from loguru import logger


SCHENGEN_COUNTRIES = {
    "Austria", "Belgium", "Czech", "Czech Republic", "Denmark", "Estonia", "Finland", "France",
    "Germany", "Greece", "Hungary", "Iceland", "Italy", "Latvia", "Liechtenstein", "Lithuania",
    "Luxembourg", "Malta", "Netherlands", "Norway", "Poland", "Portugal", "Slovakia", "Slovenia",
    "Spain", "Sweden", "Switzerland", "Croatia",
}

HEAVY_VISA_COUNTRIES = {"USA", "United States", "UK", "United Kingdom", "Britain", "England", "Canada", "Australia"}


@dataclass
class NormalizedFeatures:
    is_business: bool
    is_job_holder: bool
    business_type: Optional[str]
    business_premises: Optional[bool]
    business_online_presence: Optional[bool]
    business_assets: Optional[bool]

    is_tax_filer: Optional[bool]
    annual_income_pk: int
    closing_balance_pk: int  # 0 if unknown; if True assumed 2,000,000 handled upstream

    travel_countries: List[str]
    travel_count: int
    has_schengen_travel: bool
    has_heavy_visa: Optional[bool]
    years_since_last_travel: Optional[int]

    previous_schengen_rejection: Optional[bool]
    previous_schengen_rejection_years_ago: Optional[int]

    age: Optional[int]


def _to_bool(value: Any) -> Optional[bool]:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value).strip().lower()
    if text in {"yes", "y", "true", "1"}:
        return True
    if text in {"no", "n", "false", "0"}:
        return False
    return None


def _to_int(value: Any) -> int:
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        import re
        text = value.strip().lower()
        # Try to detect multipliers (m = million)
        if any(token in text for token in ["million", "mn", "m ", " m", "mio", "m."]):
            numbers = re.findall(r"\d+", text)
            if numbers:
                return int(numbers[0]) * 1_000_000
        # plain digits
        numbers = re.findall(r"\d+", text)
        if numbers:
            return int(numbers[0])
    return 0


def _parse_travel_countries(travel_value: Any) -> List[str]:
    if isinstance(travel_value, list):
        return [str(c).strip().title() for c in travel_value if str(c).strip()]
    if isinstance(travel_value, str):
        tl = travel_value.lower().strip()
        negative = [
            "no", "none", "never", "no history", "no travel", "no travel history",
            "never traveled", "no international travel",
        ]
        if any(p in tl for p in negative):
            return []
        parts = [p.strip() for p in travel_value.replace("/", ",").split(",")]
        return [p.title() for p in parts if p]
    return []


def _years_since(year_value: Any) -> Optional[int]:
    try:
        year = int(str(year_value).strip())
        from datetime import datetime
        current_year = datetime.now().year
        if 1900 <= year <= current_year:
            return max(0, current_year - year)
    except Exception:
        return None
    return None


def _years_since_rejection(rejection_field: Any) -> Optional[int]:
    # field can be a dict {has_rejection: bool, year: '2022'} or bool/str
    if isinstance(rejection_field, dict):
        has = _to_bool(rejection_field.get("has_rejection"))
        if not has:
            return None
        return _years_since(rejection_field.get("year")) or 99
    has = _to_bool(rejection_field)
    if not has:
        return None
    return 99


def _has_schengen_travel(countries: List[str]) -> bool:
    for c in countries:
        if any(s.lower() in c.lower() for s in SCHENGEN_COUNTRIES):
            return True
    return False


def _has_heavy_visa_from_answers(answers: Dict[str, Any], countries: List[str]) -> Optional[bool]:
    # Prefer explicit boolean if provided
    v = _to_bool(answers.get("valid_visa"))
    if v is not None:
        return v
    # Otherwise infer from travel countries (weak signal)
    for c in countries:
        if any(h.lower() in c.lower() for h in HEAVY_VISA_COUNTRIES):
            return True
    return None


def normalize_answers(answers: Dict[str, Any]) -> NormalizedFeatures:
    logger.info(f"Normalizing answers for evaluation: {answers}")

    profession = str(answers.get("profession", "")).lower()
    is_business = any(w in profession for w in ["business", "owner", "entrepreneur", "proprietor"])
    is_job_holder = any(w in profession for w in ["job", "employed", "employee", "worker", "salary"]) and not is_business
    business_type = str(answers.get("business_type") or "") or None

    business_premises = _to_bool(answers.get("business_premises"))
    business_online_presence = _to_bool(answers.get("business_online_presence"))

    is_tax_filer = _to_bool(answers.get("is_tax_filer"))
    annual_income_pk = _to_int(answers.get("annual_income"))

    closing_balance_raw = answers.get("closing_balance")
    if isinstance(closing_balance_raw, bool):
        closing_balance_pk = 2_000_000 if closing_balance_raw else 0
    else:
        closing_balance_pk = _to_int(closing_balance_raw)

    travel_countries = _parse_travel_countries(answers.get("travel_history"))
    travel_count = len(travel_countries)
    has_schengen_travel = _has_schengen_travel(travel_countries)
    has_heavy_visa = _has_heavy_visa_from_answers(answers, travel_countries)
    years_since_last_travel = _years_since(answers.get("last_travel_year"))

    prev_rej_years = _years_since_rejection(answers.get("schengen_rejection"))

    try:
        age = int(str(answers.get("age")).strip()) if answers.get("age") is not None else None
    except Exception:
        age = None

    features = NormalizedFeatures(
        is_business=is_business,
        is_job_holder=is_job_holder,
        business_type=business_type,
        business_premises=business_premises,
        business_online_presence=business_online_presence,
        business_assets=_to_bool(answers.get("business_assets")),
        is_tax_filer=is_tax_filer,
        annual_income_pk=annual_income_pk,
        closing_balance_pk=closing_balance_pk,
        travel_countries=travel_countries,
        travel_count=travel_count,
        has_schengen_travel=has_schengen_travel,
        has_heavy_visa=has_heavy_visa,
        years_since_last_travel=years_since_last_travel,
        previous_schengen_rejection=(_to_bool(answers.get("schengen_rejection"))
                                     if not isinstance(answers.get("schengen_rejection"), dict)
                                     else _to_bool(answers.get("schengen_rejection", {}).get("has_rejection"))),
        previous_schengen_rejection_years_ago=prev_rej_years,
        age=age,
    )

    logger.info(f"Normalized features: {features}")
    return features


