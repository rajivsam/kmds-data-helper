import os
from kmds_data_helper.engine import KMDS_LLM_Engine
from rich.console import Console
from rich.panel import Panel

console = Console()

def run_sequential_reports():
    # Initialize the engine (it will print the status of /documents, /data, etc.)
    engine = KMDS_LLM_Engine()

    # --- 1. THE ARCHITECT PASS (Document Analysis) ---
    if engine.active_features["pdf_processing"]:
        pdf_files = list(engine.paths["pdf_processing"].glob("*.pdf"))
        if pdf_files:
            target_pdf = str(pdf_files[0])
            console.print(f"[bold yellow][*] Phase 1: Architect Pass (Analyzing {os.path.basename(target_pdf)})...[/]")
            try:
                summary = engine.generate_summary(target_pdf)
                
                # Robust entity extraction
                raw_entities = summary.get('entities', [])
                entities_list = [str(e.get("name") if isinstance(e, dict) else e) for e in raw_entities]
                entities_str = ', '.join(entities_list)

                console.print(Panel(
                    f"[bold blue]Title:[/] {summary.get('title')}\n\n"
                    f"[bold blue]Summary:[/]\n{summary.get('summary_text')}\n\n"
                    f"[bold blue]Key Entities:[/] {entities_str}",
                    title="DATA ARCHITECT SUMMARY", border_style="blue"
                ))
            except Exception as e:
                console.print(f"[bold red][!] Architect Pass failed:[/] {e}")
    else:
        console.print("[cyan][-] Phase 1 (Architect) skipped: No PDF documents available.[/]")

    # --- 2. THE DATA SCIENTIST PASS (Quality Analysis) ---
    if engine.active_features["data_profiling"]:
        csv_files = list(engine.paths["data_profiling"].glob("**/*.csv"))
        if csv_files:
            target_csv = str(csv_files[0])
            console.print(f"\n[bold yellow][*] Phase 2: Data Scientist Pass (Analyzing {os.path.basename(target_csv)})...[/]")
            try:
                quality = engine.generate_data_report(target_csv)
                console.print(Panel(
                    f"[bold green]Quality Score:[/] {quality.get('quality_score')}\n\n"
                    f"[bold green]Observations:[/]\n{quality.get('technical_observations')}\n\n"
                    f"[bold green]Modeling Readiness:[/] {quality.get('modeling_readiness')}\n\n"
                    f"[bold red]Warnings:[/] {', '.join(quality.get('data_quality_warnings', []))}",
                    title="DATA QUALITY & READINESS REPORT", border_style="green"
                ))
            except Exception as e:
                console.print(f"[bold red][!] Scientist Pass failed:[/] {e}")
        else:
            console.print("[cyan][-] Phase 2 (Scientist) skipped: No CSV files found in data directory.[/]")
    else:
        console.print("[cyan][-] Phase 2 (Scientist) skipped: Data profiling requirements not met.[/]")

if __name__ == "__main__":
    run_sequential_reports()
