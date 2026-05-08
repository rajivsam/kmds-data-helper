import os
from kmds_data_dictionary_helper.engine import DataDictionaryEngine
from rich.console import Console
from rich.panel import Panel

console = Console()

def run_sequential_reports():
    engine = DataDictionaryEngine()
    engine.ensure_dirs()

    # --- 1. THE ARCHITECT PASS (Business Intent) ---
    pdf_files = [f for f in os.listdir(engine.pdf_dir) if f.endswith('.pdf')]
    if pdf_files:
        target_pdf = os.path.join(engine.pdf_dir, pdf_files[0])
        console.print(f"[bold yellow][*] Phase 1: Architect Pass (Document Analysis)...[/]")
        summary = engine.generate_summary(target_pdf)
        
        console.print(Panel(
            f"[bold blue]Title:[/] {summary.get('title')}\n\n"
            f"[bold blue]Summary:[/]\n{summary.get('summary_text')}\n\n"
            f"[bold blue]Key Entities:[/] {', '.join(summary.get('entities', []))}",
            title="DATA ARCHITECT SUMMARY", border_style="blue"
        ))
    else:
        console.print("[red][!] No PDF found in data/pdfs/ for Architect Pass.[/]")

    # --- 2. THE DATA SCIENTIST PASS (Technical Quality) ---
    csv_files = [f for f in os.listdir(engine.sample_dir) if f.endswith('.csv')]
    if csv_files:
        target_csv = os.path.join(engine.sample_dir, csv_files[0])
        console.print(f"\n[bold yellow][*] Phase 2: Data Scientist Pass (Quality Analysis)...[/]")
        quality = engine.generate_data_report(target_csv)
        
        console.print(Panel(
            f"[bold green]Quality Score:[/] {quality.get('quality_score')}\n\n"
            f"[bold green]Observations:[/]\n{quality.get('technical_observations')}\n\n"
            f"[bold green]Modeling Readiness:[/] {quality.get('modeling_readiness')}\n\n"
            f"[bold red]Warnings:[/] {', '.join(quality.get('data_quality_warnings', []))}",
            title="DATA QUALITY & READINESS REPORT", border_style="green"
        ))
    else:
        console.print("[red][!] No CSV found in data/samples/ for Data Scientist Pass.[/]")

if __name__ == "__main__":
    run_sequential_reports()
