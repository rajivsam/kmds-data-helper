import asyncio
import json
import time
from kmds_data_helper import PersonaAggregator
from report_generator import save_html_report 
async def main():
    # 1. Initialize - pointing to your verified workspace
    workspace = "/home/rajiv/programming/kmds_data_helper"
    aggregator = PersonaAggregator(workspace_path=workspace, max_concurrent=2)
    
    print(f"--- Starting Parallel Audit in {workspace} ---")
    print("Running Architect, Scientist, Tech Lead, and Modeling Ds...")

    # Start Timer
    start_time = time.perf_counter()

    # 2. Run the audit
    summaries = await aggregator.collect_summaries(
        context="Testing the integrated Alpha Aggregator module with time tracking.",
        stats="Verification of parallel async execution and composite JSON output."
    )
    save_html_report(summaries)
    # End Timer
    end_time = time.perf_counter()
    total_duration = end_time - start_time

    # 3. Display the result
    print("\n--- Composite Audit Results ---")
    # Uncomment the line below if you want to see the full JSON dump
    # print(json.dumps(summaries, indent=2))
    
    print(f"\nAudit complete for: {list(summaries.keys())}")
    print(f"Total Time Taken: {total_duration:.2f} seconds ({total_duration/60:.2f} minutes)")
    
    # Logic check
    if total_duration < 1800: # Less than 30 mins (your previous sequential run was 38 mins)
        print("Success: Parallel execution is significantly faster than sequential runs!")

if __name__ == "__main__":
    asyncio.run(main())
