import os
import pandas as pd
from kmds_data_dictionary_helper.engine import DataDictionaryEngine
from rich.console import Console
from rich.panel import Panel

console = Console()

def main():
    engine = DataDictionaryEngine()
    engine.ensure_dirs()
    
    # --- PHASE 1: THE ARCHITECT (PDF Summary) ---
    pdf_files = [f for f in os.listdir(engine.pdf_dir) if f.endswith('.pdf')]
    if pdf_files:
        console.print("[bold yellow][*] Running Architect Pass...[/]")
        # Safe indexing for the target PDF
        target_pdf = os.path.join(engine.pdf_dir, pdf_files[0])
        try:
            summary = engine.generate_summary(target_pdf)
            console.print(Panel(
                f"[bold blue]Business Intent:[/] {summary.get('summary_text')}\n\n"
                f"[bold blue]Key Entities:[/] {', '.join(summary.get('entities', []))}",
                title=f"ARCHITECT: {summary.get('title')}", border_style="blue"
            ))
        except Exception as e:
            console.print(f"[bold red][!] Architect Pass failed:[/] {e}")
    else:
        console.print("[bold red][!] No PDFs found in data/pdfs. Skipping Architect Pass.[/]")
    
    # --- PHASE 2: THE SCIENTIST (Data Quality) ---
    csv_files = [f for f in os.listdir(engine.sample_dir) if f.endswith('.csv')]
    if csv_files:
        console.print("\n[bold yellow][*] Running Data Scientist Pass...[/]")
        target_csv = os.path.join(engine.sample_dir, csv_files[0])
        try:
            quality = engine.generate_data_report(target_csv)
            console.print(Panel(
                f"[bold green]Readiness:[/] {quality.get('modeling_readiness')}\n\n"
                f"[bold red]Warnings:[/] {', '.join(quality.get('data_quality_warnings', []))}",
                title="SCIENTIST: Data Quality Report", border_style="green"
            ))
        except Exception as e:
            console.print(f"[bold red][!] Scientist Pass failed:[/] {e}")
    else:
        console.print("[bold red][!] No CSVs found in data/samples. Skipping Scientist Pass.[/]")

    # --- PHASE 3: THE ENGINEER (Deep Extraction) ---
    console.print("\n[bold yellow][*] Running Deep Field Extraction...[/]")
    
    # Gather Ground Truth
    all_truth = []
    for f in csv_files:
        all_truth.extend(engine.get_data_ground_truth(os.path.join(engine.sample_dir, f)))

    # Handle reference TXT files if any exist
    txt_files = [f for f in os.listdir(engine.sample_dir) if f.endswith('.txt')]
    for f in txt_files:
        all_truth.extend(engine.get_data_ground_truth(os.path.join(engine.sample_dir, f)))

    # Final Mapping
    all_definitions = []
    for f in pdf_files:
        defs = engine.extract_definitions(os.path.join(engine.pdf_dir, f), ground_truth=all_truth)
        if defs:
            all_definitions.extend(defs)

    # Final Save with safety against KeyErrors
    if all_definitions:
        output_path = os.path.join(engine.data_dir, "kmds_output.csv")
        df = pd.DataFrame(all_definitions)
        
        # Ensure 'field_name' exists (Engine should handle this, but we check anyway)
        if 'field_name' in df.columns:
            df = df.drop_duplicates(subset=['field_name'])
            df.to_csv(output_path, index=False)
            console.print(f"\n[bold green][✔] Success![/] Dictionary with {len(df)} fields saved to {output_path}")
        else:
            console.print("[bold red][!] Error: LLM extraction returned invalid schema.[/]")
    else:
        console.print("[bold red][!] No definitions were extracted. Check Ollama connectivity.[/]")

if __name__ == "__main__":
    main()
