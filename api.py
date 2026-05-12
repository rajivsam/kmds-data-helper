from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import traceback

# Internal imports
from kmds_data_helper.service import KMDSReportService
from kmds_data_helper.llm_client import LLMClient

app = FastAPI(title="KMDS v2 Analysis Service")

class AnalysisRequest(BaseModel):
    # Allows client to point to any valid workspace root
    config_path: str = "data" 
    output_dir: str = "output"

@app.post("/analyze")
async def analyze(request: AnalysisRequest):
    """
    Orchestrates the audit request. 
    Validation is handled by the Service layer before execution.
    """
    try:
        # 1. Initialize the LLM client pointed at the specific workspace
        # This ensures the folder-based persona discovery works
        client_instance = LLMClient(config_path=request.config_path)

        # 2. Initialize Service (this triggers the strict directory validation)
        service = KMDSReportService(
            llm_client=client_instance,
            config_path=request.config_path,
            output_dir=request.output_dir
        )

        # 3. Await the full multi-notebook, multi-persona audit
        results = await service.run_full_audit()
        
        return results

    except ValueError as ve:
        # Catch validation failures (missing folders/files)
        # Returns 400 with the diagnostic message from Service
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        # Catch-all for unexpected crashes, with traceback for debugging
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/health")
async def health():
    return {"status": "online", "version": "v2.0-baseline"}
