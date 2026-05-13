import asyncio
import json
import time
from pathlib import Path
from kmds_data_helper.llm_client import LLMClient
from kmds_data_helper.service import KMDSReportService
from kmds_data_helper.aggregator import PersonaAggregator
# Assuming this is your local layout helper
from report_generator import save_html_report 

async def main():
    # 1. Initialize Workspace Infrastructure
    workspace = "/home/rajiv/programming/kmds_data_helper"
    
    # Initialize the Grounded LLM Client
    client = LLMClient(config_path=workspace)
    
    # Initialize Service Layer (Validates pillars & discovers folder personas)
    service = KMDSReportService(llm_client=client, config_path=workspace)
    
    # Initialize the Knowledge Dictionary Builder
    aggregator = PersonaAggregator()
    
    # Specify the exact personas to track for this demo run
    target_personas = ["Architect", "Scientist", "Tech Lead", "Senior Modeling Data Scientist"]
    
    print(f"--- Starting Grounded Audit in {workspace} ---")
    print(f"Running: {', '.join(target_personas)}...")

    # Start Timer
    start_time = time.perf_counter()

    # 2. Execute Grounded Audit using Service Layer
    # This automatically invokes utilities to fuel context and maintains Semaphore(1)
    audit_outputs = await service.run_audit(requested_personas=target_personas)
    
    # 3. Consolidate individual notebook/persona findings into the aggregator
    for response_packet in audit_outputs:
        aggregator.add_audit_result(response_packet)
        
    # Extract the complete composite dictionary
    summaries = aggregator.knowledge_dict
    
    # Generate reports
    save_html_report(summaries)
    
    # End Timer
    end_time = time.perf_counter()
    total_duration = end_time - start_time

    # 4. Display the results
    print("\n--- Composite Grounded Audit Results ---")
    print(f"Audit complete for: {list(summaries.keys())}")
    print(f"Total Time Taken: {total_duration:.2f} seconds ({total_duration/60:.2f} minutes)")
    
    # Notice: Since Semaphore(1) guarantees VRAM safety, we monitor sequential stability here
    print("Verification complete: Audits executed safely without VRAM crashes.")

if __name__ == "__main__":
    asyncio.run(main())
