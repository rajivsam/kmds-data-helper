from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

# Correcting the import to match the standard class naming convention
from kmds_data_helper.service import KMDSReportService
from kmds_data_helper.llm_client import LLMClient

app = FastAPI(title="KMDS v2 Analysis Service")

class AnalysisRequest(BaseModel):
    # This field allows the client to point to 'data', 'data2', or '../kmds_2_data_helper'
    config_path: Optional[str] = "data" 
    output_dir: str = "output"

@app.post("/analyze")
async def analyze(request: AnalysisRequest):
    """
    Initializes the KMDS service dynamically for each request.
    """
    try:
        # Initialize the LLM client instance
        client_instance = LLMClient()

        # The Service gatekeeper validates the config_path here
        service = KMDSReportService(
            llm_client=client_instance,
            config_path=request.config_path,
            output_dir=request.output_dir
        )

        # Run the full audit using the dynamic configuration
        results = service.run_full_audit()
        
        return results

    except ValueError as ve:
        # Returns the clear "Diagnostic Report" from our Service layer
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/health")
async def health():
    return {"status": "online", "version": "v2.0-baseline"}
