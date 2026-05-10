import requests
import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def test_kmds_api():
    url = "http://localhost:8000/analyze"
    
    # Points to your workspace copy
    payload = {
        "config_path": "../kmds_2_data_helper", 
        "output_dir": "./output"
    }

    console.print(f"[dim]Debug - Target URL: {url}[/]")
    console.print(Panel(f"[bold cyan]KMDS API Test Client[/]\nTarget: {url}\nWorkspace: {payload['config_path']}", border_style="cyan"))

    try:
        with console.status("[bold green]Running deep analysis... (LLMs are thinking hard)") as status:
            response = requests.post(url, json=payload, timeout=600)
            data = response.json()

            if response.status_code == 400:
                detail = data.get("detail", str(data)) if isinstance(data, dict) else str(data)
                console.print(Panel(f"[bold red]Configuration Validation Failed[/]\n\n{detail}", 
                                    title="[bold white]Server Diagnostic Report[/]", border_style="red"))
                return

            response.raise_for_status()

        # Handle Success: data is a LIST of notebook results
        notebook_list = data if isinstance(data, list) else []

        table = Table(title="\nStage 1: Multi-Persona Notebook Insights", show_header=True, header_style="bold white")
        table.add_column("Notebook", style="cyan")
        table.add_column("Score", justify="center", style="green")
        table.add_column("Modeling DS (Exploratory Insight)", style="yellow")

        for nb in notebook_list:
            # 1. Get the raw insight blocks
            sci_data = nb.get("scientist_insight", {})
            mod_data = nb.get("modeling_ds_insight", {}) # Note: Using 'modeling_ds_insight' to match your persona key

            # 2. FUZZY MATCH SCORE: Try various keys the LLM might use
            sci_score = (
                sci_data.get("quality_score") or 
                sci_data.get("score") or 
                sci_data.get("scientific_rigor_score") or 
                "N/A"
            )

            # 3. FUZZY MATCH INSIGHT: Try various keys for the summary
            mod_text = (
                mod_data.get("exploratory_summary") or 
                mod_data.get("summary") or 
                mod_data.get("model_justification") or 
                "No insight found"
            )
            
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

    except Exception as e:
        console.print(f"[bold red][!] API Client Error:[/] {str(e)}")

if __name__ == "__main__":
    test_kmds_api()
