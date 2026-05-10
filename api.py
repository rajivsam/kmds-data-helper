import os
import sys
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kmds_api")

# Bridge the path to src
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

try:
    from kmds_data_helper.service import KMDSReportService
    from kmds_data_helper.llm_client import LLMClient
except ImportError as e:
    logger.error(f"Import Error: {e}. Ensure 'uv pip install -e .' was run.")
    sys.exit(1)

app = FastAPI(title="KMDS Data Helper API", version="2.0.0")

# --- Pydantic Models with Defaults to prevent 500 Errors ---

class NotebookDetail(BaseModel):
    notebook_name: str
    # Using Field(default_factory=...) ensures every notebook has these keys
    scientist_insight: Dict[str, Any] = Field(
        default_factory=lambda: {"quality_score": 0, "insight": "No data"}
    )
    modeling_insight: Dict[str, Any] = Field(
        default_factory=lambda: {"exploratory_summary": "No data", "model_justification": "N/A"}
    )

class AnalysisResponse(BaseModel):
    status: str
    project_summary: Dict[str, Any] = Field(
        default_factory=lambda: {"strategic_alignment": "N/A", "production_roadmap": "N/A"}
    )
    notebook_details: List[NotebookDetail]
    metadata: Dict[str, Any]

class AnalysisRequest(BaseModel):
    notebook_dir: str = "./notebooks"
    output_dir: str = "./output"

# Global service instance
kmds_service = None

@app.on_event("startup")
async def startup_event():
    global kmds_service
    try:
        llm_client = LLMClient(config_path="kmds_config.yaml")
        kmds_service = KMDSReportService(llm_client=llm_client)
        logger.info("[*] KMDS Service initialized.")
    except Exception as e:
        logger.error(f"[!] Init failure: {e}")

@app.post("/analyze", response_model=AnalysisResponse)
async def run_analysis(request: AnalysisRequest):
    if kmds_service is None:
        raise HTTPException(status_code=503, detail="Service not initialized.")

    try:
        logger.info(f"[*] Starting analysis for: {request.notebook_dir}")
        kmds_service.output_dir = Path(request.output_dir)
        report = kmds_service.generate_comprehensive_report(request.notebook_dir)
        return report
    except Exception as e:
        logger.exception("Analysis failed:") 
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/report/latest")
async def get_latest_report():
    if not kmds_service: raise HTTPException(status_code=503)
    report = kmds_service.get_last_report()
    if not report: raise HTTPException(status_code=404)
    return report

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
