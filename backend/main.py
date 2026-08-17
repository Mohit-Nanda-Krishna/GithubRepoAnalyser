from fastapi import FastAPI
from pydantic import BaseModel
from github_fetcher import fetch_repo_data
from agents.code_agent import analyze_code_quality
from agents.docs_agent import analyze_documentation
from agents.health_agent import analyze_repo_health
from agents.synthesizer import synthesize_report

app = FastAPI()

class AnalyzeRequest(BaseModel):
    repo_url: str

@app.post("/analyze")
async def analyze_repo(request: AnalyzeRequest):
    try:
        data = fetch_repo_data(request.repo_url)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    docs_result = analyze_documentation(data)
    health_result = analyze_repo_health(data)
    code_result = analyze_code_quality(data)
    final_report = synthesize_report(
        data["basics"], code_result, docs_result, health_result
    )
    return {"report": final_report}