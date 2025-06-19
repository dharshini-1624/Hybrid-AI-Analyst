from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv
from hybrid_ai_analyst.analyzer import HybridAIAnalyzer
import tempfile
import shutil
import json

# Loading environment variables
load_dotenv()

app = FastAPI(
    title="Hybrid AI Analyst",
    description="AI-powered startup vetting system that analyzes both qualitative and quantitative data",
    version="1.0.0"
)

# Initializing the analyzer
analyzer = HybridAIAnalyzer()

@app.get("/")
async def root():
    return {"message": "Hybrid AI Analyst - Startup Vetting System"}

@app.post("/vet_startup")
async def vet_startup(
    memo_file: UploadFile = File(..., description="Text file containing company memo or article"),
    financial_data: UploadFile = File(..., description="CSV file containing financial data")
):
    
    # Analyzing a startup using both qualitative (text memo) and quantitative (financial data) analysis.
    
    try:
        print(f"\n Received analysis request:")
        print(f"   Memo file: {memo_file.filename}")
        print(f"   Financial data: {financial_data.filename}")
        print("=" * 60)
        
        # Validating file types
        if not memo_file.filename.endswith('.txt'):
            raise HTTPException(status_code=400, detail="Memo file must be a .txt file")
        
        if not financial_data.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Financial data must be a .csv file")
        
        # Creating temporary files to store uploaded content
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.txt', delete=False) as memo_temp:
            shutil.copyfileobj(memo_file.file, memo_temp)
            memo_path = memo_temp.name
        
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as csv_temp:
            shutil.copyfileobj(financial_data.file, csv_temp)
            csv_path = csv_temp.name
        
        try:
            print(" Processing files with Hybrid AI Analyzer...")
            
            # Performing the hybrid analysis
            result = await analyzer.analyze_startup(memo_path, csv_path)
            
            print("\n Analysis completed successfully!")
            print("=" * 60)
            print(" ANALYSIS RESULTS:")
            print("=" * 60)
            
            # Printing the analysis results in server terminal
            print(f"\n Qualitative Summary:")
            print("-" * 40)
            print(result['qualitative_summary'][:300] + "..." if len(result['qualitative_summary']) > 300 else result['qualitative_summary'])
            
            print(f"\n Quantitative Summary:")
            print("-" * 40)
            print(result['quantitative_summary'])
            
            print(f"\n Final Recommendation:")
            print("-" * 40)
            recommendation = result['final_recommendation']
            print(f"Decision: {recommendation['decision']}")
            print(f"Justification: {recommendation['justification']}")
            
            print("\n" + "=" * 60)
            print(" Returning JSON response to client...")
            print("=" * 60)
            print("\n JSON output returned to client:")
            print(json.dumps(result, indent=2))
            return JSONResponse(content=result, status_code=200)
            
        finally:
            # Cleaning up temporary files
            os.unlink(memo_path)
            os.unlink(csv_path)
            
    except Exception as e:
        print(f" Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/health")
async def health_check():
    # Health check endpoint
    return {"status": "healthy", "service": "Hybrid AI Analyst"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 