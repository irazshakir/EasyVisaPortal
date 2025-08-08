"""
Evaluation service for visa application assessment
Provides clean interface for scenario-based evaluations
"""
from typing import Dict, Any, Optional
from loguru import logger

from app.services.rag_service import rag_service, ScenarioEvaluation
from app.services.evaluation.normalizer import normalize_answers
from app.services.evaluation.rubric import score_profile
from app.services.evaluation.narrative import build_narrative


class EvaluationService:
    """Service for handling visa application evaluations"""
    
    def __init__(self):
        self.rag_service = rag_service
    
    async def evaluate_visa_application(self, user_answers: Dict[str, Any], target_country: str = None) -> Dict[str, Any]:
        """
        Evaluate visa application using deterministic rubric (no scenario selection here).
        """
        try:
            logger.info(f"Starting rubric-based evaluation for country: {target_country}")
            logger.info(f"User answers: {user_answers}")

            features = normalize_answers(user_answers)
            evaluation_result = score_profile(features)

            logger.info(f"Rubric evaluation completed with success ratio: {evaluation_result.get('success_ratio')}%")
            return evaluation_result

        except Exception as e:
            logger.error(f"Error in rubric evaluation: {e}")
            return self._get_fallback_evaluation()
    
    # -----------------------
    # Human-like formatting helpers
    # -----------------------
    def _normalize_bool(self, value: Any) -> Optional[bool]:
        """Attempt to normalize a value to boolean or None."""
        try:
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
        except Exception:
            pass
        return None

    def _extract_travel_info(self, user_answers: Dict[str, Any]) -> Dict[str, Any]:
        """Extract travel-related info in a tolerant way."""
        travel = user_answers.get("travel_history", [])
        last_year = user_answers.get("last_travel_year")

        # Normalize travel list
        countries: list[str] = []
        if isinstance(travel, list):
            countries = [str(c).strip().title() for c in travel if str(c).strip()]
        elif isinstance(travel, str):
            tl = travel.lower().strip()
            negative = [
                "no", "none", "never", "no history", "no travel", "no travel history",
                "never traveled", "no international travel"
            ]
            if any(p in tl for p in negative):
                countries = []
            else:
                # naive split on commas and slashes
                parts = [p.strip() for p in travel.replace("/", ",").split(",")]
                countries = [p.title() for p in parts if p]

        return {
            "countries": countries,
            "has_travel": len(countries) > 0,
            "last_year": str(last_year) if last_year else None,
        }

    def _schengen_coverage(self, countries: list[str]) -> Dict[str, bool]:
        schengen_set = {
            "Austria","Belgium","Czech","Czech Republic","Denmark","Estonia","Finland","France",
            "Germany","Greece","Hungary","Iceland","Italy","Latvia","Liechtenstein","Lithuania",
            "Luxembourg","Malta","Netherlands","Norway","Poland","Portugal","Slovakia","Slovenia",
            "Spain","Sweden","Switzerland","Croatia"
        }
        has_schengen_travel = any(any(s.lower() in c.lower() for s in schengen_set) for c in countries)
        return {"has_schengen_travel": has_schengen_travel}

    def _visa_type_recommendation(self, answers: Dict[str, Any]) -> str:
        """Heuristic visa type recommendation based on profile."""
        profession = str(answers.get("profession", "")).lower()
        valid_heavy = self._normalize_bool(answers.get("valid_visa"))
        travel_info = self._extract_travel_info(answers)
        schengen_flags = self._schengen_coverage(travel_info["countries"])

        # Prefer Business for first-time Schengen with no heavy visas
        if not schengen_flags["has_schengen_travel"] and not valid_heavy:
            return "Apply for a Business visa rather than Tourist for your first Schengen application."

        # If clearly a business profile, still recommend Business where possible
        if any(w in profession for w in ["business", "owner", "entrepreneur", "proprietor"]):
            return "Given your business profile, a Business visa is recommended where applicable."

        return "Tourist or Business can both work; choose the one that best matches your purpose with strong documentation."

    def _country_strategy_line(self, answers: Dict[str, Any]) -> str:
        """Provide a pragmatic country targeting tip for Schengen."""
        # Default pragmatic guidance
        avoid = ["Germany", "France", "Italy"]
        prefer = ["Belgium", "Netherlands", "Norway", "Spain"]

        travel_info = self._extract_travel_info(answers)
        valid_heavy = self._normalize_bool(answers.get("valid_visa"))
        schengen_flags = self._schengen_coverage(travel_info["countries"])

        # If no strong prior (first-time Schengen and no heavy visas), include the avoid/prefer advice
        if not schengen_flags["has_schengen_travel"] and not valid_heavy:
            return (
                f"For Schengen, avoid initial applications to {', '.join(avoid)}. "
                f"Start with relatively approachable countries like {', '.join(prefer)}."
            )
        return "Select a Schengen country that aligns with your purpose and documentation strength."

    def _build_human_like_message(
        self,
        evaluation: Dict[str, Any],
        user_answers: Dict[str, Any],
        target_country: Optional[str]
    ) -> str:
        """Create a concise, human-style narrative using the scenario evaluation and answers."""
        # Basics
        country = (
            user_answers.get("selected_country")
            or user_answers.get("country")
            or target_country
        )

        success_ratio = evaluation.get("success_ratio")
        confidence_label = evaluation.get("confidence_level") or "Medium"

        # Extract signals
        travel_info = self._extract_travel_info(user_answers)
        travel_countries = travel_info["countries"]
        last_year = travel_info["last_year"]
        has_travel = travel_info["has_travel"]
        valid_heavy = self._normalize_bool(user_answers.get("valid_visa"))
        profession = str(user_answers.get("profession", "")).strip()
        business_type = str(user_answers.get("business_type", "")).strip()
        is_tax_filer = self._normalize_bool(user_answers.get("is_tax_filer"))
        annual_income = user_answers.get("annual_income")
        closing_balance = user_answers.get("closing_balance")

        # Schengen first-time signal
        schengen_flags = self._schengen_coverage(travel_countries)
        first_time_schengen = not schengen_flags["has_schengen_travel"]

        # Lines
        intro = (
            f"Thanks for sharing your details. Based on your information, here’s our assessment"
            + (f" for {country}." if country else ":")
        )

        ratio_line = (
            f"Current success ratio: {success_ratio}% (Confidence: {confidence_label})."
            if success_ratio is not None else ""
        )

        # 1) Visa type recommendation
        visa_type_line = self._visa_type_recommendation(user_answers)
        first_time_line = ""
        if first_time_schengen and (valid_heavy is False or valid_heavy is None):
            first_time_line = (
                "This looks like your first Schengen application and you don’t hold a valid US/UK/Canada/Australia visa."
            )

        # 2) Travel history perspective
        if has_travel:
            travels = ", ".join(travel_countries[:6])  # keep concise
            travel_line = (
                f"You have a reasonable travel history (e.g., {travels})"
                + (f" and your last trip was in {last_year}." if last_year else ".")
            )
        else:
            travel_line = (
                "You don’t appear to have international travel history yet; that can reduce early approval odds unless other areas are strong."
            )

        # 2b) Country strategy
        country_strategy = self._country_strategy_line(user_answers)

        # 3) Purpose guidance
        purpose_line = (
            "Have a clear and verifiable purpose (event, exhibition, client meetings, or a formal business invitation)."
        )

        # 4) Documentation line
        ties_line_parts = []
        if profession:
            ties_line_parts.append(f"Profile: {profession}" + (f" ({business_type})." if business_type else "."))
        if is_tax_filer is True:
            if annual_income:
                ties_line_parts.append(f"Tax filer with declared income ~ {annual_income} PKR.")
            else:
                ties_line_parts.append("Tax filer (keep recent returns ready).")
        if isinstance(closing_balance, (int, float)) and closing_balance:
            ties_line_parts.append(f"Bank balance around {int(closing_balance):,} PKR.")
        elif closing_balance is True:
            ties_line_parts.append("You can maintain the required closing balance.")

        ties_prefix = "On documentation, show strong ties with your homeland to ensure visa success."
        ties_suffix = (" " + " ".join(ties_line_parts)).strip()
        ties_line = (ties_prefix + (" " + ties_suffix if ties_suffix else ""))

        # Scenario-specific tips (top 2-3)
        scenario_recs = evaluation.get("recommendations", []) or []
        scenario_tips = [f"- {r}" for r in scenario_recs[:3]]

        # Build numbered guidance
        points: list[str] = []
        p1 = "; ".join([s for s in [first_time_line, visa_type_line] if s])
        if p1:
            points.append(f"1 - {p1}")
        else:
            points.append(f"1 - {visa_type_line}")

        points.append(f"2 - {travel_line} {country_strategy}")
        points.append(f"3 - {purpose_line}")
        points.append(f"4 - {ties_line}")

        # Add scenario tips if available
        if scenario_tips:
            points.append("Additionally, keep in mind:")
            points.extend(scenario_tips)

        closing = (
            "These are our recommendations. You can now generate a tailored checklist or discuss with our AI Consultant for file preparation."
        )

        parts = [intro]
        if ratio_line:
            parts.append(ratio_line)
        parts.extend(points)
        parts.append(closing)

        return "\n".join(parts)
    
    def _format_evaluation_result(self, scenario_eval: ScenarioEvaluation, user_answers: Dict[str, Any]) -> Dict[str, Any]:
        """Format the evaluation result for presentation"""
        
        # Determine overall recommendation
        if scenario_eval.success_ratio >= 80:
            overall_recommendation = "Strong approval likelihood - Proceed with application"
            confidence_level = "High"
        elif scenario_eval.success_ratio >= 60:
            overall_recommendation = "Good approval likelihood - Apply with proper preparation"
            confidence_level = "Medium"
        elif scenario_eval.success_ratio >= 40:
            overall_recommendation = "Moderate approval likelihood - Consider improvements first"
            confidence_level = "Medium"
        else:
            overall_recommendation = "Low approval likelihood - Build profile before applying"
            confidence_level = "Low"
        
        # Create detailed response
        result = {
            "success_ratio": scenario_eval.success_ratio,
            "overall_recommendation": overall_recommendation,
            "confidence_level": confidence_level,
            "matched_scenario": scenario_eval.matched_scenario,
            "strengths": scenario_eval.strengths,
            "risk_factors": scenario_eval.risk_factors,
            "recommendations": scenario_eval.recommendations,
            "application_strategy": scenario_eval.application_strategy,
            "required_documents": scenario_eval.required_documents,
            "confidence": scenario_eval.confidence,
            "should_apply": scenario_eval.success_ratio >= 60,
            "next_steps": self._generate_next_steps(scenario_eval, user_answers)
        }
        
        return result
    
    def _generate_next_steps(self, scenario_eval: ScenarioEvaluation, user_answers: Dict[str, Any]) -> list:
        """Generate specific next steps based on evaluation"""
        next_steps = []
        
        if scenario_eval.success_ratio >= 80:
            next_steps.extend([
                "Prepare all required documents",
                "Book visa appointment",
                "Consider using our AI portal for document preparation",
                "Ensure travel insurance is arranged"
            ])
        elif scenario_eval.success_ratio >= 60:
            next_steps.extend([
                "Work on strengthening weak areas",
                "Prepare comprehensive documentation",
                "Consider professional consultation",
                "Use our AI portal for guidance"
            ])
        else:
            next_steps.extend([
                "Build travel history first",
                "Strengthen financial profile",
                "Establish business ties",
                "Consider alternative destinations"
            ])
        
        # Add scenario-specific steps
        if "no travel history" in [rf.lower() for rf in scenario_eval.risk_factors]:
            next_steps.append("Start with easier destinations like Turkey, Malaysia, or Singapore")
        
        if "low income" in [rf.lower() for rf in scenario_eval.risk_factors]:
            next_steps.append("Focus on building financial stability and documentation")
        
        return next_steps
    
    def _get_fallback_evaluation(self) -> Dict[str, Any]:
        """Provide fallback evaluation when main evaluation fails"""
        return {
            "success_ratio": 50,
            "overall_recommendation": "Unable to complete evaluation - Please try again",
            "confidence_level": "Low",
            "matched_scenario": "General Profile",
            "strengths": ["Basic eligibility"],
            "risk_factors": ["Unable to perform detailed analysis"],
            "recommendations": ["Please ensure all required documents are properly prepared"],
            "application_strategy": "Apply with complete documentation and professional assistance",
            "required_documents": ["Passport", "CNIC", "Bank Statement", "Employment Letter"],
            "confidence": 0.5,
            "should_apply": False,
            "next_steps": ["Contact support for assistance", "Ensure all information is provided"]
        }
    
    async def get_evaluation_summary(self, user_answers: Dict[str, Any], target_country: str = None) -> str:
        """
        Get a human-like, concise narrative summary based on the rubric evaluation and collected answers.
        
        Args:
            user_answers: Dictionary containing user's responses
            target_country: Target country for visa application
            
        Returns:
            Human-readable narrative string
        """
        try:
            # If the FSM already stored an evaluation for this session, reuse it to avoid duplicate work
            evaluation = user_answers.get("evaluation")
            if not evaluation or not isinstance(evaluation, dict) or "success_ratio" not in evaluation:
                evaluation = await self.evaluate_visa_application(user_answers, target_country)

            # Build deterministic narrative; optionally, a later step could pass this to RAG for polishing
            return build_narrative(evaluation, user_answers, target_country)
            
        except Exception as e:
            logger.error(f"Error generating evaluation summary: {e}")
            return (
                "Thanks for sharing your details. I wasn’t able to complete a full evaluation right now. "
                "Please try again in a moment or contact support if the issue persists."
            )


# Global evaluation service instance
evaluation_service = EvaluationService()
