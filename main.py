import os
import sys
import json
from pathlib import Path

# 1. Bridge the path to the src folder
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# 2. Import the new modular Orchestrator
from kmds_data_helper.engine import KMDSEngine
from rich.console import Console
from rich.panel import Panel

console = Console()

def main():
    # 3. Initialize Engine (Uses kmds_config.yaml for paths)
    try:
        engine = KMDSEngine()
    except Exception as e:
        console.print(f"[bold red][!] Initialization failed:[/] {e}")
        return

    # --- PHASE 1: THE ARCHITECT (PDF & Documentation) ---
    # We check the active features inside the data_processor module now
    if engine.data.active_features.get("pdf_processing"):
        console.print("[bold yellow][*] Running Architect Pass...[/]")
        pdf_files = list(engine.config.paths["docs"].glob("*.pdf"))

        if pdf_files:
            target_pdf = str(pdf_files[0])
            try:
                # Assuming you still want a quick summary
                # (You might need to port the old generate_summary to the new Engine class if missing)
                summary = engine.llm.ask_persona('architect', context=os.path.basename(target_pdf), stats="Initial Scan")
                
                entities = [str(e.get("name") if isinstance(e, dict) else e)
                            for e in summary.get('entities', [])]

                console.print(Panel(
                    f"[bold blue]Business Intent:[/] {summary.get('summary_text')}\n\n"
                    f"[bold blue]Key Entities:[/] {', '.join(entities)}",
                    title=f"ARCHITECT: {summary.get('title')}", border_style="blue"
                ))
            except Exception as e:
                console.print(f"[bold red][!] Architect Pass failed:[/] {e}")

    # --- PHASE 2: THE SCIENTIST ---
    if engine.data.active_features.get("data_profiling"):
        console.print("\n[bold yellow][*] Running Data Scientist Pass...[/]")
        # Ground truth check (Isolation Test)
        truth = engine.data.get_ground_truth()
        csv_sources = [t['source'] for t in truth if 'columns' in t]
        
        if csv_sources:
            console.print(f"[green][+] Profiling active on:[/] {', '.join(csv_sources)}")
            # For the scientist report, we just use the first valid source
            try:
                # Using the modular llm call
                quality = engine.llm.ask_persona('scientist', context=csv_sources[0], stats="Profiling complete")
                
                console.print(Panel(
                    f"[bold green]Quality Score:[/] {quality.get('quality_score')}\n\n"
                    f"[bold green]Readiness:[/] {quality.get('modeling_readiness')}",
                    title="SCIENTIST: Data Quality Report", border_style="green"
                ))
            except Exception as e:
                console.print(f"[bold red][!] Scientist Pass failed:[/] {e}")

    # --- PHASE 3: THE DEVELOPMENT PASS ---
    if engine.data.active_features.get("notebook_analysis"):
        console.print("\n[bold yellow][*] Running Development Pass (Notebook Analysis)...[/]")
        try:
            dev_report = engine.run_development_pass()
            summary = dev_report["project_summary"]

            debt = [str(d) for d in summary.get('technical_debt_warnings', [])]

            console.print(Panel(
                f"[bold blue]Health:[/] {summary.get('project_health')}\n"
                f"[bold green]Deployment Readiness:[/] {summary.get('deployment_readiness_score')}/10\n"
                f"[bold red]Critical Debt:[/] {', '.join(debt) if debt else 'None'}",
                title="TECH LEAD: Project Synthesis", border_style="magenta"
            ))
        except Exception as e:
            console.print(f"[bold red][!] Development Pass failed:[/] {e}")

if __name__ == "__main__":
    main()
