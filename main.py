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
    if engine.data.active_features.get("pdf_processing"):
        console.print("[bold yellow][*] Running Architect Pass...[/]")
        pdf_files = list(engine.config.paths["docs"].glob("*.pdf"))

        if pdf_files:
            target_pdf = str(pdf_files[0])
            try:
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
        truth = engine.data.get_ground_truth()
        csv_sources = [t['source'] for t in truth if 'columns' in t]
        
        if csv_sources:
            console.print(f"[green][+] Profiling active on:[/] {', '.join(csv_sources)}")
            try:
                quality = engine.llm.ask_persona('scientist', context=csv_sources[0], stats="Profiling complete")
                
                console.print(Panel(
                    f"[bold green]Quality Score:[/] {quality.get('quality_score')}\n\n"
                    f"[bold green]Readiness:[/] {quality.get('modeling_readiness')}",
                    title="SCIENTIST: Data Quality Report", border_style="green"
                ))
            except Exception as e:
                console.print(f"[bold red][!] Scientist Pass failed:[/] {e}")

    # --- PHASE 3: THE DEVELOPMENT PASS (STRATEGIC SYNTHESIS) ---
    if engine.data.active_features.get("notebook_analysis"):
        console.print("\n[bold yellow][*] Running Development Pass (Multi-Persona Synthesis)...[/]")
        try:
            # dev_report now contains individual_notebook_reports AND strategic_summary
            dev_report = engine.run_development_pass()
            
            # The Engine returns 'strategic_summary', let's grab it safely
            summary = dev_report.get("strategic_summary", {})

            # Handle the keys defined in your consolidated YAML for strategic_lead
            alignment = summary.get('strategic_alignment', 'No alignment data')
            roadmap = summary.get('production_roadmap', 'No roadmap provided')
            risks = [str(r) for r in summary.get('scalability_risks', [])]

            console.print(Panel(
                f"[bold blue]Strategic Alignment:[/] {alignment}\n\n"
                f"[bold green]Production Roadmap:[/] {roadmap}\n\n"
                f"[bold red]Scalability Risks:[/] {', '.join(risks) if risks else 'None Identified'}",
                title="STRATEGIC TECH LEAD: Project Roadmap", border_style="magenta"
            ))
            
            console.print(f"\n[bold green]✅ Full JSON artifacts available in:[/] {engine.config.paths['output']}")

        except Exception as e:
            console.print(f"[bold red][!] Development Pass UI Display failed:[/] {e}")
            console.print("[yellow][i]Note: The analysis likely finished; check output folder for JSON.[/]")

if __name__ == "__main__":
    main()
