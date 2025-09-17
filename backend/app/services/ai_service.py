import google.generativeai as genai
from typing import Dict, Any, List, Optional
import json
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class GeminiAIService:
    def __init__(self):
        """Initialize Gemini AI service with API key."""
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def analyze_marine_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze marine biodiversity data using Gemini AI."""
        try:
            prompt = self._create_analysis_prompt(data)
            response = self.model.generate_content(prompt)
            
            return {
                "analysis": response.text,
                "insights": self._extract_insights(response.text),
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error analyzing marine data: {str(e)}")
            return {
                "error": f"AI analysis failed: {str(e)}",
                "status": "error"
            }
    
    async def generate_conservation_recommendations(self, species_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate conservation recommendations based on species data."""
        try:
            prompt = f"""
            Based on the following marine species data, provide conservation recommendations:
            
            Species Data: {json.dumps(species_data, indent=2)}
            
            Please provide:
            1. Conservation status assessment
            2. Threat analysis
            3. Specific conservation recommendations
            4. Monitoring strategies
            5. Priority actions
            
            Format the response as detailed recommendations for marine conservation efforts.
            """
            
            response = self.model.generate_content(prompt)
            
            return {
                "recommendations": response.text,
                "priority_level": self._assess_priority(response.text),
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error generating conservation recommendations: {str(e)}")
            return {
                "error": f"Conservation analysis failed: {str(e)}",
                "status": "error"
            }
    
    async def explain_biodiversity_patterns(self, occurrence_data: Dict[str, Any]) -> Dict[str, Any]:
        """Explain biodiversity patterns from occurrence data."""
        try:
            prompt = f"""
            Analyze the following marine biodiversity occurrence data and explain the patterns:
            
            Data: {json.dumps(occurrence_data, indent=2)}
            
            Please explain:
            1. Geographic distribution patterns
            2. Species diversity trends
            3. Ecological relationships
            4. Environmental correlations
            5. Potential impacts of climate change
            
            Provide insights in clear, scientific language suitable for researchers and policymakers.
            """
            
            response = self.model.generate_content(prompt)
            
            return {
                "explanation": response.text,
                "key_patterns": self._extract_patterns(response.text),
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error explaining biodiversity patterns: {str(e)}")
            return {
                "error": f"Pattern analysis failed: {str(e)}",
                "status": "error"
            }
    
    async def chat_about_marine_data(self, question: str, context_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Interactive chat about marine data and biodiversity."""
        try:
            context_prompt = ""
            if context_data:
                context_prompt = f"\nContext Data: {json.dumps(context_data, indent=2)}\n"
            
            prompt = f"""
            You are a marine biology and biodiversity expert. Answer the following question about marine ecosystems and biodiversity:
            
            Question: {question}
            {context_prompt}
            
            Provide a comprehensive, scientifically accurate answer that includes:
            1. Direct answer to the question
            2. Relevant scientific context
            3. Current research insights
            4. Practical implications
            5. Further research suggestions if applicable
            
            Keep the answer informative yet accessible.
            """
            
            response = self.model.generate_content(prompt)
            
            return {
                "answer": response.text,
                "confidence": "high",  # Could be enhanced with actual confidence scoring
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error in marine data chat: {str(e)}")
            return {
                "error": f"Chat analysis failed: {str(e)}",
                "status": "error"
            }
    
    def _create_analysis_prompt(self, data: Dict[str, Any]) -> str:
        """Create analysis prompt for marine data."""
        return f"""
        Analyze the following marine biodiversity data and provide insights:
        
        Data: {json.dumps(data, indent=2)}
        
        Please provide:
        1. Summary of the data
        2. Key biodiversity indicators
        3. Species richness analysis
        4. Geographic distribution insights
        5. Conservation implications
        6. Data quality assessment
        7. Research recommendations
        
        Focus on scientifically relevant patterns and conservation priorities.
        """
    
    def _extract_insights(self, analysis_text: str) -> List[str]:
        """Extract key insights from analysis text."""
        # This is a simple implementation - could be enhanced with NLP
        insights = []
        lines = analysis_text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['key', 'important', 'significant', 'notable', 'critical']):
                insights.append(line.strip())
        return insights[:5]  # Return top 5 insights
    
    def _assess_priority(self, recommendations_text: str) -> str:
        """Assess conservation priority level."""
        text_lower = recommendations_text.lower()
        if any(word in text_lower for word in ['urgent', 'critical', 'immediate', 'emergency']):
            return "high"
        elif any(word in text_lower for word in ['important', 'significant', 'moderate']):
            return "medium"
        else:
            return "low"
    
    def _extract_patterns(self, explanation_text: str) -> List[str]:
        """Extract key patterns from explanation text."""
        patterns = []
        lines = explanation_text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['pattern', 'trend', 'distribution', 'correlation']):
                patterns.append(line.strip())
        return patterns[:5]  # Return top 5 patterns

# Global AI service instance
ai_service = GeminiAIService()