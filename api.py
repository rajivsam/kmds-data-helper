from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import traceback

# Internal imports
from kmds_data_helper.service import KMDSReportService
from kmds_data_helper.llm_client import LLMClient

app = FastAPI(title="KMDS v2 Analysis Service")

class AnalysisRequest(BaseModel):
    # Allows client to point to any valid workspace root
    config_path: str = "data" 
    output_dir: str = "output"
    # ROADMAP: Support subset filtering for personas (e.g., ["Architect", "Scientist"])
    requested_personas: Optional[List[str]] = None
    # Optional: Filter for specific notebooks
    notebook_paths: Optional[List[str]] = None

@app.post("/analyze")
async def analyze(request: AnalysisRequest):
    """
    Orchestrates the audit request. 
    Now supports subset filtering for personas and notebooks.
    """
    try:
        # 1. Initialize the LLM client pointed at the specific workspace
        client_instance = LLMClient(config_path=request.config_path)

        # 2. Initialize Service (triggers strict directory validation)
        service = KMDSReportService(
            llm_client=client_instance,
            config_path=request.config_path,
            output_dir=request.output_dir
        )

        # 3. Call the updated run_audit with filtering support
        # This replaces run_full_audit() to allow for requested_personas
        results = await service.run_audit(
            notebook_paths=request.notebook_paths,
            requested_personas=request.requested_personas
        )
        
        return results

    except ValueError as ve:
        # Catch validation failures or missing persona YAMLs
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        # Catch-all for unexpected crashes
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/health")
async def health():
    return {"status": "online", "version": "v2.0-baseline"}
