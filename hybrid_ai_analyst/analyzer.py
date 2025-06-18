import asyncio
import os
from typing import Dict, Any
from .qualitative_analyzer import QualitativeAnalyzer
from .quantitative_analyzer import QuantitativeAnalyzer
from .synthesis_engine import SynthesisEngine

class HybridAIAnalyzer:
    """
    Main orchestrator for the Hybrid AI Analyst system.
    Coordinates parallel qualitative and quantitative analysis pipelines,
    then synthesizes results into a final investment recommendation.
    """
    
    def __init__(self):
        """Initialize the analyzer components"""
        self.qualitative_analyzer = QualitativeAnalyzer()
        self.quantitative_analyzer = QuantitativeAnalyzer()
        self.synthesis_engine = SynthesisEngine()
    
    async def analyze_startup(self, memo_path: str, csv_path: str) -> Dict[str, Any]:
        """
        Perform comprehensive startup analysis using both qualitative and quantitative data.
        
        Args:
            memo_path: Path to the text file containing company memo
            csv_path: Path to the CSV file containing financial data
            
        Returns:
            Dictionary containing qualitative_summary, quantitative_summary, and final_recommendation
        """
        try:
            # Running both analysis pipelines in parallel
            qualitative_task = asyncio.create_task(
                self.qualitative_analyzer.analyze_memo(memo_path)
            )
            quantitative_task = asyncio.create_task(
                self.quantitative_analyzer.analyze_financial_data(csv_path)
            )
            
            
            qualitative_summary, quantitative_summary = await asyncio.gather(
                qualitative_task, quantitative_task
            )
            
            # Synthesizing the results into final recommendation
            final_recommendation = await self.synthesis_engine.synthesize_recommendation(
                qualitative_summary, quantitative_summary
            )
            
            return {
                "qualitative_summary": qualitative_summary,
                "quantitative_summary": quantitative_summary,
                "final_recommendation": final_recommendation
            }
            
        except Exception as e:
            raise Exception(f"Analysis failed: {str(e)}")
    
    async def get_analysis_status(self) -> Dict[str, Any]:
        """Get the status of all analyzer components"""
        return {
            "qualitative_analyzer": await self.qualitative_analyzer.get_status(),
            "quantitative_analyzer": await self.quantitative_analyzer.get_status(),
            "synthesis_engine": await self.synthesis_engine.get_status()
        } 