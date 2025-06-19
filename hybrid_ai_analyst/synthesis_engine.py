import asyncio
import os
from typing import Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class SynthesisEngine:
    
    def __init__(self):
        # Initializing the synthesis engine with LLM
        # Initializing Gemini API 
        api_key = os.getenv("GOOGLE_API_KEY")
        self.use_llm = api_key and api_key != "your_google_api_key_here"
        
        if self.use_llm:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
            except Exception as e:
                print(f"Warning: LLM initialization failed: {e}")
                self.use_llm = False
    
    async def synthesize_recommendation(
        self, 
        qualitative_summary: str, 
        quantitative_summary: str
    ) -> Dict[str, str]:
        
        # Synthesizing qualitative and quantitative insights into final investment recommendation
        
        try:
            if self.use_llm:
                print("LLM mode: Using Gemini for synthesis")
                # Creating synthesis prompt
                prompt = self._create_synthesis_prompt(qualitative_summary, quantitative_summary)
                
                # Generating final recommendation
                try:
                    response = await asyncio.to_thread(
                        self.model.generate_content, prompt
                    )
                    # Parsing the response
                    recommendation = self._parse_recommendation_response(response.text)
                except Exception as e:
                    print(f"LLM call failed (synthesis): {e}")
                    recommendation = self._fallback_synthesis(qualitative_summary, quantitative_summary)
            else:
                print("Fallback mode: Using rule-based synthesis")
                # Using fallback synthesis
                recommendation = self._fallback_synthesis(qualitative_summary, quantitative_summary)
            
            return recommendation
            
        except Exception as e:
            print(f"Synthesis failed: {str(e)}")
            # Fallback to rule-based synthesis if LLM fails
            return self._fallback_synthesis(qualitative_summary, quantitative_summary)
    
    def _create_synthesis_prompt(self, qualitative_summary: str, quantitative_summary: str) -> str:
        
        # Creating the synthesis prompt for the LLM.
        
        prompt = f"""
        You are an experienced venture capitalist. Given the following qualitative and quantitative summaries, provide a final investment recommendation. State whether you would 'Invest', 'Pass', or 'Monitor', and provide a 2-3 sentence justification for your decision.
        
        QUALITATIVE SUMMARY:
        {qualitative_summary}
        
        QUANTITATIVE SUMMARY:
        {quantitative_summary}
        
        Provide your final investment recommendation in the following format:
        
        DECISION: [Choose exactly one: "Invest", "Pass", or "Monitor"]
        
        JUSTIFICATION: [Provide a 2-3 sentence justification explaining your decision, referencing specific factors from both analyses]
        """
        
        return prompt
    
    def _parse_recommendation_response(self, response_text: str) -> Dict[str, str]:
    
        # Parse the LLM response to extract decision and justification.
        
        try:
            # Extracting decision
            decision = None
            if "DECISION:" in response_text:
                decision_line = [line for line in response_text.split('\n') if 'DECISION:' in line][0]
                decision = decision_line.split('DECISION:')[1].strip()
            elif "Invest" in response_text and "Pass" not in response_text and "Monitor" not in response_text:
                decision = "Invest"
            elif "Pass" in response_text and "Invest" not in response_text and "Monitor" not in response_text:
                decision = "Pass"
            elif "Monitor" in response_text and "Invest" not in response_text and "Pass" not in response_text:
                decision = "Monitor"
            else:
                # Default to Monitor if unclear
                decision = "Monitor"
            
            # Extracting justification
            justification = ""
            if "JUSTIFICATION:" in response_text:
                justification_line = [line for line in response_text.split('\n') if 'JUSTIFICATION:' in line][0]
                justification = justification_line.split('JUSTIFICATION:')[1].strip()
            else:
                # Extracting the last few sentences as justification
                sentences = response_text.split('.')
                justification = '. '.join(sentences[-3:]).strip()
            
            return {
                "decision": decision,
                "justification": justification
            }
            
        except Exception as e:
            # Fallback parsing
            return {
                "decision": "Monitor",
                "justification": f"Analysis completed but response parsing failed: {response_text[:200]}..."
            }
    
    def _fallback_synthesis(self, qualitative_summary: str, quantitative_summary: str) -> Dict[str, str]:
        
        #Fallback synthesis method when LLM is unavailable.
        
        # Simple rule-based decision making
        decision = "Monitor"
        justification_parts = []
        
        # Check for positive indicators
        positive_indicators = 0
        
        # Qualitative indicators
        if any(word in qualitative_summary.lower() for word in ['strong', 'experienced', 'expert', 'innovative']):
            positive_indicators += 1
            justification_parts.append("Strong qualitative indicators")
        
        if any(word in qualitative_summary.lower() for word in ['market', 'opportunity', 'growth']):
            positive_indicators += 1
            justification_parts.append("Market opportunity identified")
        
        # Quantitative indicators
        if 'growth' in quantitative_summary.lower() and 'decline' not in quantitative_summary.lower():
            positive_indicators += 1
            justification_parts.append("Positive growth metrics")
        
        if 'stable' in quantitative_summary.lower() or 'consistent' in quantitative_summary.lower():
            positive_indicators += 1
            justification_parts.append("Stable financial performance")
        
        # Decision logic
        if positive_indicators >= 3:
            decision = "Invest"
        elif positive_indicators >= 2:
            decision = "Monitor"
        else:
            decision = "Pass"
        
        justification = f"Rule-based analysis: {', '.join(justification_parts)}. Decision: {decision}."
        
        return {
            "decision": decision,
            "justification": justification
        }
    
    async def get_status(self) -> Dict[str, Any]:
        # Get the status of the synthesis engine
        return {
            "status": "operational",
            "llm": "Google Gemini Pro" if self.use_llm else "Fallback mode (no API key)",
            "synthesis_method": "LLM-based with fallback rules"
        } 