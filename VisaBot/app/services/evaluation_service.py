"""
Evaluation service for visa application assessment
Provides clean interface for scenario-based evaluations
"""
from typing import Dict, Any, Optional
from loguru import logger

from app.services.rag_service import rag_service, ScenarioEvaluation


class EvaluationService:
    """Service for handling visa application evaluations"""
    
    def __init__(self):
        self.rag_service = rag_service
    
    async def evaluate_visa_application(self, user_answers: Dict[str, Any], target_country: str = None) -> Dict[str, Any]:
        """
        Evaluate visa application using scenario-based approach
        
        Args:
            user_answers: Dictionary containing user's responses
            target_country: Target country for visa application
            
        Returns:
            Dictionary containing evaluation results
        """
        try:
            logger.info(f"Starting visa application evaluation for country: {target_country}")
            logger.info(f"User answers: {user_answers}")
            
            # Perform scenario-based evaluation
            scenario_evaluation = await self.rag_service.perform_scenario_based_evaluation(
                user_answers, target_country
            )
            
            # Format the response
            evaluation_result = self._format_evaluation_result(scenario_evaluation, user_answers)
            
            logger.info(f"Evaluation completed with success ratio: {scenario_evaluation.success_ratio}%")
            
            return evaluation_result
            
        except Exception as e:
            logger.error(f"Error in visa application evaluation: {e}")
            return self._get_fallback_evaluation()
    
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
        Get a formatted summary of the evaluation for display
        
        Args:
            user_answers: Dictionary containing user's responses
            target_country: Target country for visa application
            
        Returns:
            Formatted string summary
        """
        try:
            evaluation = await self.evaluate_visa_application(user_answers, target_country)
            
            summary_parts = []
            summary_parts.append(f"🎯 **Visa Evaluation Result**")
            summary_parts.append(f"Success Ratio: {evaluation['success_ratio']}%")
            summary_parts.append(f"Recommendation: {evaluation['overall_recommendation']}")
            summary_parts.append(f"Confidence: {evaluation['confidence_level']}")
            summary_parts.append("")
            
            if evaluation['strengths']:
                summary_parts.append("✅ **Your Strengths:**")
                for strength in evaluation['strengths'][:3]:  # Limit to top 3
                    summary_parts.append(f"• {strength}")
                summary_parts.append("")
            
            if evaluation['risk_factors']:
                summary_parts.append("⚠️ **Areas to Address:**")
                for risk in evaluation['risk_factors'][:3]:  # Limit to top 3
                    summary_parts.append(f"• {risk}")
                summary_parts.append("")
            
            if evaluation['recommendations']:
                summary_parts.append("📋 **Recommendations:**")
                for rec in evaluation['recommendations'][:5]:  # Limit to top 5
                    summary_parts.append(f"• {rec}")
                summary_parts.append("")
            
            summary_parts.append("👉 **Next Steps:**")
            for i, step in enumerate(evaluation['next_steps'][:4], 1):  # Limit to top 4
                summary_parts.append(f"{i}. {step}")
            summary_parts.append("")
            
            summary_parts.append("Thank you for using Easy Visa PK! For detailed assistance, contact our visa experts.")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Error generating evaluation summary: {e}")
            return "Unable to generate evaluation summary. Please try again or contact support."


# Global evaluation service instance
evaluation_service = EvaluationService()
