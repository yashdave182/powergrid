from groq import Groq
from typing import Dict, List, Optional, Any
from app.config import settings
import logging
import json

logger = logging.getLogger(__name__)

class GroqLLMService:
    """Service for integrating Groq LLM for enhanced data retrieval and analysis"""
    
    def __init__(self):
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = "mixtral-8x7b-32768"  # High-performance model for data analysis
    
    async def analyze_marine_data(self, data: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Analyze marine data using LLM and provide insights"""
        try:
            prompt = self._create_analysis_prompt(data, query)
            
            completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a marine biology and oceanography expert. Analyze the provided data and provide scientific insights, patterns, and recommendations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=1024
            )
            
            analysis_result = completion.choices[0].message.content
            
            return {
                "analysis": analysis_result,
                "confidence": "high",
                "data_points_analyzed": len(str(data)),
                "query": query
            }
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return {
                "analysis": "Analysis failed due to technical error",
                "confidence": "low",
                "error": str(e)
            }
    
    async def generate_species_insights(self, species_data: List[Dict]) -> Dict[str, Any]:
        """Generate insights about species diversity and distribution"""
        try:
            species_summary = self._summarize_species_data(species_data)
            
            prompt = f"""
            Analyze the following marine species data and provide insights:
            
            Species Data Summary:
            {species_summary}
            
            Please provide:
            1. Biodiversity assessment
            2. Distribution patterns
            3. Conservation status insights
            4. Ecosystem health indicators
            5. Recommendations for further research
            """
            
            completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a marine biodiversity expert. Provide scientific analysis of species data focusing on conservation and ecosystem health."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.2,
                max_tokens=1024
            )
            
            insights = completion.choices[0].message.content
            
            return {
                "insights": insights,
                "species_count": len(species_data),
                "analysis_type": "biodiversity_assessment"
            }
            
        except Exception as e:
            logger.error(f"Species insights generation failed: {e}")
            return {"error": str(e)}
    
    async def interpret_oceanographic_data(self, ocean_data: Dict[str, Any]) -> Dict[str, Any]:
        """Interpret oceanographic measurements and trends"""
        try:
            prompt = f"""
            Analyze the following oceanographic data and provide scientific interpretation:
            
            Data: {json.dumps(ocean_data, indent=2)}
            
            Please analyze:
            1. Temperature and salinity patterns
            2. Chemical composition implications
            3. Climate change indicators
            4. Impact on marine ecosystems
            5. Data quality assessment
            """
            
            completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an oceanographer expert. Interpret oceanographic data and explain its significance for marine ecosystems and climate."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.2,
                max_tokens=1024
            )
            
            interpretation = completion.choices[0].message.content
            
            return {
                "interpretation": interpretation,
                "data_type": "oceanographic",
                "parameters_analyzed": list(ocean_data.keys()) if isinstance(ocean_data, dict) else []
            }
            
        except Exception as e:
            logger.error(f"Oceanographic data interpretation failed: {e}")
            return {"error": str(e)}
    
    async def suggest_research_directions(self, combined_data: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest research directions based on integrated data analysis"""
        try:
            prompt = f"""
            Based on the integrated marine data provided, suggest research directions and hypotheses:
            
            Integrated Data Summary:
            {json.dumps(combined_data, indent=2)[:2000]}...
            
            Please suggest:
            1. Priority research questions
            2. Data gaps to address
            3. Interdisciplinary research opportunities
            4. Policy implications
            5. Technology recommendations
            """
            
            completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a marine science research strategist. Suggest impactful research directions based on available data."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.4,
                max_tokens=1024
            )
            
            suggestions = completion.choices[0].message.content
            
            return {
                "research_suggestions": suggestions,
                "data_integration_score": self._calculate_integration_score(combined_data)
            }
            
        except Exception as e:
            logger.error(f"Research suggestions generation failed: {e}")
            return {"error": str(e)}
    
    def _create_analysis_prompt(self, data: Dict[str, Any], query: str) -> str:
        """Create a structured prompt for data analysis"""
        data_summary = str(data)[:1500]  # Limit data size for prompt
        
        return f"""
        User Query: {query}
        
        Marine Data to Analyze:
        {data_summary}
        
        Please provide a comprehensive analysis addressing the user's query with scientific accuracy.
        Focus on patterns, correlations, and actionable insights.
        """
    
    def _summarize_species_data(self, species_data: List[Dict]) -> str:
        """Summarize species data for LLM analysis"""
        if not species_data:
            return "No species data available"
        
        summary = {
            "total_species": len(species_data),
            "sample_species": species_data[:5],  # First 5 species as example
            "data_fields": list(species_data[0].keys()) if species_data else []
        }
        
        return json.dumps(summary, indent=2)
    
    def _calculate_integration_score(self, data: Dict[str, Any]) -> float:
        """Calculate a score representing data integration completeness"""
        if not data:
            return 0.0
        
        data_types = len(data.keys())
        data_points = sum(len(str(v)) for v in data.values())
        
        # Simple scoring based on data diversity and volume
        return min(1.0, (data_types * 0.2) + (data_points / 10000))

# Global LLM service instance
llm_service = GroqLLMService()