import os
import pandas as pd
from kmds_data_helper.engine import KMDS_LLM_Engine
from rich.console import Console
from rich.panel import Panel

console = Console()


def main():
    # 1. Initialize Engine (Auto-checks /documents, /data, /notebooks)
    engine = KMDS_LLM_Engine()

    # 2. PHASE 1: THE ARCHITECT (PDF & Documentation)
    if engine.active_features["pdf_processing"]:
        console.print("[bold yellow][*] Running Architect Pass...[/]")
        pdf_files = list(engine.paths["pdf_processing"].glob("*.pdf"))

        if pdf_files:
            target_pdf = str(pdf_files[0])
            try:
                summary = engine.generate_summary(target_pdf)
                # Robust entity extraction logic
                entities = [str(e.get("name") if isinstance(e, dict) else e)
                            for e in summary.get('entities', [])]

                console.print(Panel(
                    f"[bold blue]Business Intent:[/] {summary.get('summary_text')}\n\n"
                    f"[bold blue]Key Entities:[/] {', '.join(entities)}",
                    title=f"ARCHITECT: {summary.get('title')}", border_style="blue"
                ))
            except Exception as e:
                console.print(f"[bold red][!] Architect Pass failed:[/] {e}")

    # --- PHASE 2: THE SCIENTIST (Updated with Warning Fix) ---
    if engine.active_features["data_profiling"]:
        console.print("\n[bold yellow][*] Running Data Scientist Pass...[/]")
        csv_files = [f for f in engine.paths["data_profiling"].glob("**/*.csv")
                     if "kmds_output" not in f.name]

        if csv_files:
            target_csv = str(csv_files[0])
            try:
                quality = engine.generate_data_report(target_csv)

                # Robustly handle list of strings or dicts in warnings
                raw_warnings = quality.get('data_quality_warnings', [])
                warnings = [str(w.get("message") if isinstance(
                    w, dict) else w) for w in raw_warnings]

                console.print(Panel(
                    f"[bold green]Quality Score:[/] {quality.get('quality_score')}\n\n"
                    f"[bold green]Readiness:[/] {quality.get('modeling_readiness')}\n\n"
                    f"[bold red]Warnings:[/] {', '.join(warnings) if warnings else 'None'}",
                    title="SCIENTIST: Data Quality Report", border_style="green"
                ))
            except Exception as e:
                console.print(f"[bold red][!] Scientist Pass failed:[/] {e}")

    # --- PHASE 4: THE DEVELOPMENT PASS (Integrated) ---
    if engine.active_features["notebook_analysis"]:
        console.print(
            "\n[bold yellow][*] Running Development Pass (Notebook Analysis)...[/]")
        try:
            dev_report = engine.run_development_pass()
            summary = dev_report["project_summary"]

            # Robustly handle technical debt list
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
