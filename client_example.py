#!/usr/bin/env python3
"""
Client example for the Hybrid AI Analyst API.
This script demonstrates how to use the /vet_startup endpoint.
"""

import requests
import json
import os
from pathlib import Path

def test_api_endpoint():
    """Test the /vet_startup API endpoint with sample data."""
    
    # API endpoint
    url = "http://localhost:8000/vet_startup"
    
    # Sample data files
    memo_file = "sample_data/company_memo.txt"
    csv_file = "sample_data/financial_data.csv"
    
    # Checking if files exist
    if not os.path.exists(memo_file):
        print(f" Memo file not found: {memo_file}")
        return False
    
    if not os.path.exists(csv_file):
        print(f" CSV file not found: {csv_file}")
        return False
    
    try:
        # Preparing files for upload
        files = {
            'memo_file': ('company_memo.txt', open(memo_file, 'rb'), 'text/plain'),
            'financial_data': ('financial_data.csv', open(csv_file, 'rb'), 'text/csv')
        }
        
        print(" Sending request to Hybrid AI Analyst API...")
        print(f"   URL: {url}")
        print(f"   Files: {memo_file}, {csv_file}")
        
        # Making the request
        response = requests.post(url, files=files)
        
        # Checking response
        if response.status_code == 200:
            result = response.json()
            
            print("\n Analysis completed successfully!")
            print("=" * 50)
            
            # Displaying results
            print(f"\n Qualitative Summary:")
            print("-" * 30)
            print(result['qualitative_summary'])
            
            print(f"\n Quantitative Summary:")
            print("-" * 30)
            print(result['quantitative_summary'])
            
            print(f"\n Final Recommendation:")
            print("-" * 30)
            recommendation = result['final_recommendation']
            print(f"Decision: {recommendation['decision']}")
            print(f"Justification: {recommendation['justification']}")
            
            return True
            
        else:
            print(f" API request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(" Could not connect to the API server.")
        print("   Make sure the server is running: python main.py")
        return False
        
    except Exception as e:
        print(f" Error: {str(e)}")
        return False

def test_health_endpoint():
    """Testing the health check endpoint."""
    
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("Health check passed")
            return True
        else:
            print(f"Health check failed: {response.status_code}")
            return False
    except:
        print("Health check failed - server not running")
        return False

def main():
    """Main function."""
    
    print(" Hybrid AI Analyst - API Client Example")
    print("=" * 50)
    
    # Testing health endpoint first
    if not test_health_endpoint():
        print("\nTo start the server, run: python main.py")
        return
    
    # Testing the main endpoint
    success = test_api_endpoint()
    
    if success:
        print("\n API test completed successfully!")
        print("\n You can now:")
        print("1. Use your own data files")
        print("2. Integrate with your applications")
        print("3. Build custom clients")
    else:
        print("\n API test failed. Check the server logs for details.")

if __name__ == "__main__":
    main() 