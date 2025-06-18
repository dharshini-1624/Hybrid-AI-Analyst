#!/usr/bin/env python3
"""
Test script for the Hybrid AI Analyst system.
This script tests the system with sample data to ensure all components work correctly.
"""

import asyncio
import os
import sys
from pathlib import Path

# Adding the project root to the Python path
sys.path.append(str(Path(__file__).parent))

from hybrid_ai_analyst.analyzer import HybridAIAnalyzer

async def test_analysis():
    """Testing the complete analysis pipeline with sample data."""
    
    print(" Testing Hybrid AI Analyst System")
    print("=" * 50)
    
    # Checking if sample data exists
    memo_path = "sample_data/company_memo.txt"
    csv_path = "sample_data/financial_data.csv"
    
    if not os.path.exists(memo_path):
        print(f" Sample memo file not found: {memo_path}")
        return False
    
    if not os.path.exists(csv_path):
        print(f" Sample CSV file not found: {csv_path}")
        return False
    
    print(f" Found sample data files")
    
    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_google_api_key_here":
        print("⚠️  Google API key not set. Using fallback analysis mode.")
        print("   Set GOOGLE_API_KEY environment variable for full LLM analysis.")
    
    try:
        # Initializing analyzer
        print(" Initializing Hybrid AI Analyzer...")
        analyzer = HybridAIAnalyzer()
        
        # Testing status
        print(" Checking component status...")
        status = await analyzer.get_analysis_status()
        for component, info in status.items():
            print(f"   {component}: {info.get('status', 'unknown')}")
        
        # Running analysis
        print(" Running analysis...")
        result = await analyzer.analyze_startup(memo_path, csv_path)
        
        # Displaying results
        print("\n Analysis Results:")
        print("-" * 30)
        
        print(f"\n Qualitative Summary:")
        print(result['qualitative_summary'][:200] + "..." if len(result['qualitative_summary']) > 200 else result['qualitative_summary'])
        
        print(f"\n Quantitative Summary:")
        print(result['quantitative_summary'])
        
        print(f"\n Final Recommendation:")
        recommendation = result['final_recommendation']
        print(f"   Decision: {recommendation['decision']}")
        print(f"   Justification: {recommendation['justification']}")
        
        print("\n Analysis completed successfully!")
        return True
        
    except Exception as e:
        print(f" Analysis failed: {str(e)}")
        return False

async def test_components():
    """Testing individual components."""
    
    print("\n Testing Individual Components")
    print("=" * 40)
    
    try:
        from hybrid_ai_analyst.qualitative_analyzer import QualitativeAnalyzer
        from hybrid_ai_analyst.quantitative_analyzer import QuantitativeAnalyzer
        from hybrid_ai_analyst.synthesis_engine import SynthesisEngine
        
        # Testing quantitative analyzer (doesn't require API key)
        print(" Testing Quantitative Analyzer...")
        quant_analyzer = QuantitativeAnalyzer()
        status = await quant_analyzer.get_status()
        print(f"   Status: {status['status']}")
        
        # Testing with sample CSV
        csv_path = "sample_data/financial_data.csv"
        if os.path.exists(csv_path):
            summary = await quant_analyzer.analyze_financial_data(csv_path)
            print(f"   Sample analysis: {summary[:100]}...")
        
        print(" Component tests completed!")
        return True
        
    except Exception as e:
        print(f" Component test failed: {str(e)}")
        return False

def main():
    """Main test function."""
    
    print(" Hybrid AI Analyst - System Test")
    print("=" * 50)
    
    # Running tests
    success = asyncio.run(test_components())
    if success:
        asyncio.run(test_analysis())
    
    print("\n Test completed!")
    print("\n Next steps:")
    print("1. Set your GOOGLE_API_KEY environment variable")
    print("2. Run 'python main.py' to start the server")
    print("3. Visit http://localhost:8000/docs for API documentation")
    print("4. Use the /vet_startup endpoint with your own data")

if __name__ == "__main__":
    main() 