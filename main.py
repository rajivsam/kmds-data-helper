import os
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

# Bridge the path to the src folder so we can import the package
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# Import the new service-oriented components
from kmds_data_helper.service import KMDSReportService
from kmds_data_helper.llm_client import LLMClient  # Ensure this class exists in your src

console = Console()

def main():
    """
    Main entry point refactored to use the KMDSReportService.
    This demonstrates the 'Service-First' approach for local execution.
    """
    console.print(Panel.fit(
        "[bold cyan]KMDS Data Helper v2.0[/]\n[italic]Service-Oriented Multi-Persona Analysis[/]",
        border_style="blue"
    ))

    # 1. Configuration Paths
    config_path = "kmds_config.yaml"
    notebook_dir = "./notebooks"
    output_dir = "./output"

    if not os.path.exists(config_path):
        console.print(f"[bold red][!] Error:[/] Configuration file '{config_path}' not found.")
        return

    try:
        # 2. Initialize the Infrastructure
        # We initialize the LLMClient (which reads the config) and pass it to the Service
        console.print("[*] Initializing LLM Client and KMDS Service...")
        llm_client = LLMClient(config_path=config_path)
        service = KMDSReportService(llm_client=llm_client, output_dir=output_dir)

        # 3. Execute Full Pipeline via the Service
        # This one call replaces the manual Stage 1 / Stage 2 loops
        console.print(f"[*] Starting analysis on notebooks in: [bold white]{notebook_dir}[/]")
        report = service.generate_comprehensive_report(notebook_dir=notebook_dir)

        # 4. Success Output
        # Extract the strategic summary for the console view
        strat_report = report.get("project_summary", {})
        
        console.print("\n")
        console.print(Panel(
            f"[bold blue]Strategic Alignment:[/]\n{strat_report.get('strategic_alignment', 'N/A')}\n\n"
            f"[bold red]Scalability Risks:[/]\n{', '.join(strat_report.get('scalability_risks', [])) if isinstance(strat_report.get('scalability_risks'), list) else strat_report.get('scalability_risks', 'N/A')}\n\n"
            f"[bold green]Production Roadmap:[/]\n{strat_report.get('production_roadmap', 'N/A')}",
            title="[bold magenta]STRATEGIC TECH LEAD: Project Roadmap[/]",
            border_style="magenta",
            padding=(1, 2)
        ))

        console.print(f"\n[bold green]✅ Full JSON artifacts available in:[/] {report['metadata']['output_directory']}")
        console.print(f"[bold green]✅ Service Report saved to:[/] {output_dir}/full_service_report.json")

    except FileNotFoundError as e:
        console.print(f"[bold red][!] Path Error:[/] {e}")
    except Exception as e:
        console.print(f"[bold red][!] Critical Failure during service execution:[/] {str(e)}")
        import traceback
        console.print(traceback.format_exc())

if __name__ == "__main__":
    main()
