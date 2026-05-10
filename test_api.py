import requests
import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def test_kmds_api():
    url = "http://localhost:8000/analyze"
    payload = {
        "notebook_dir": "./notebooks",
        "output_dir": "./output"
    }

    console.print(f"[dim]Debug - Target URL: {url}[/]")
    console.print(Panel(f"[bold cyan]KMDS API Test Client[/]\nTarget: {url}", border_style="cyan"))

    try:
        # Increased timeout to 600 seconds (10 minutes) to allow for multiple LLM passes
        with console.status("[bold green]Running deep analysis... (LLMs are thinking hard)") as status:
            response = requests.post(url, json=payload, timeout=600)
            response.raise_for_status()
            data = response.json()

        # Strategic Summary View
        strat = data.get("project_summary", {})
        strat_align = strat.get('strategic_alignment', 'No alignment data found.')
        roadmap = strat.get('production_roadmap', 'No roadmap provided.')

        console.print(Panel(
            f"[bold blue]Strategic Alignment:[/]\n{strat_align}\n\n"
            f"[bold green]Production Roadmap:[/]\n{roadmap}",
            title="[bold magenta]API RESPONSE: Strategic Lead[/]",
            border_style="magenta"
        ))

        # Notebook Insights Table
        table = Table(title="\nStage 1: Multi-Persona Notebook Insights", show_header=True, header_style="bold white")
        table.add_column("Notebook", style="cyan")
        table.add_column("Score", justify="center", style="green")
        table.add_column("Modeling DS (Exploratory Insight)", style="yellow")

        for nb in data.get("notebook_details", []):
            sci_data = nb.get("scientist_insight", {})
            mod_data = nb.get("modeling_insight", {})
            
            sci_score = sci_data.get("quality_score", "N/A")
            mod_text = mod_data.get("exploratory_summary", "No insight found")
            
            display_text = str(mod_text)
            if len(display_text) > 100:
                display_text = display_text[:97] + "..."
            
            table.add_row(
                nb.get("notebook_name", "Unknown"), 
                str(sci_score), 
                display_text
            )

        console.print(table)
        console.print(f"\n[bold green]✅ Success: Analysis Complete.[/]")

    except requests.exceptions.Timeout:
        console.print("[bold red][!] Client Timeout:[/] The server is taking longer than 10 minutes. Check Terminal 1 logs.")
    except Exception as e:
        console.print(f"[bold red][!] API Test Failed:[/] {str(e)}")

if __name__ == "__main__":
    test_kmds_api()
