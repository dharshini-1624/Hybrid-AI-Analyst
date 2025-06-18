#!/usr/bin/env python3
"""
Simple API test - no dependencies on other test files
"""

import requests
import json

def test_api():
    """Test the API endpoint directly"""
    
    url = "http://localhost:8000/vet_startup"
    
    # Sample data files
    files = {
        'memo_file': ('company_memo.txt', open('sample_data/company_memo.txt', 'rb'), 'text/plain'),
        'financial_data': ('financial_data.csv', open('sample_data/financial_data.csv', 'rb'), 'text/csv')
    }
    
    
    print("🚀 Testing API endpoint directly...")
    print(f"URL: {url}")
    print("=" * 60)
    
    try:
        
        response = requests.post(url, files=files)  
        
        if response.status_code == 200:
            result = response.json()
            
            print("Server returned JSON successfully!")
            print("=" * 60)
            print("JSON Response:")
            print(json.dumps(result, indent=2))
            
            print("\n" + "=" * 60)
            print("Summary:")
            print(f"   Qualitative Summary: {len(result['qualitative_summary'])} characters")
            print(f"   Quantitative Summary: {len(result['quantitative_summary'])} characters")
            print(f"   Decision: {result['final_recommendation']['decision']}")
            print(f"   Justification: {len(result['final_recommendation']['justification'])} characters")
            
        else:
            print(f"API request failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_api() 