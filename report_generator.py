import json
from datetime import datetime
import textwrap

def save_html_report(summaries: dict, filename: str = "audit_report.html"):
    html_template = """
    <html>
    <head>
        <title>KMDS Persona Audit Report</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background: #f0f2f5; color: #333; }}
            .container {{ max-width: 1000px; margin: auto; }}
            .persona-group {{ margin-bottom: 40px; }}
            .persona-title {{ color: #1a1a1a; border-bottom: 2px solid #0056b3; padding-bottom: 5px; margin-bottom: 15px; }}
            .card {{ background: white; padding: 25px; margin-bottom: 15px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid #0056b3; }}
            h1 {{ color: #1a1a1a; text-align: center; margin-bottom: 5px; }}
            h3 {{ color: #444; margin-top: 0; display: flex; justify-content: space-between; align-items: center; }}
            .status-tag {{ font-size: 0.7em; background: #e7f3ff; color: #0056b3; padding: 4px 12px; border-radius: 20px; }}
            pre {{ background: #1e1e1e; color: #dcdcdc; padding: 20px; border-radius: 8px; overflow-x: auto; font-size: 14px; line-height: 1.5; }}
            .meta {{ text-align: center; color: #666; margin-bottom: 40px; font-style: italic; }}
            .error {{ border-left: 5px solid #dc3545; }}
            .error h3 {{ color: #dc3545; }}
            .error .status-tag {{ background: #fdf2f2; color: #dc3545; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>KMDS Data Helper: Persona Audit Report</h1>
            <p class="meta">Generated at: {timestamp}</p>
            {content}
        </div>
    </body>
    </html>
    """
    
    content_html = ""
    
    # 1. Outer Loop: Iterate through each tracked Persona
    for persona, notebooks in summaries.items():
        content_html += f'<div class="persona-group">'
        content_html += f'<h2 class="persona-title">{persona}</h2>'
        
        # 2. Inner Loop: Extract individual notebook findings matching the persona
        for notebook_name, insight in notebooks.items():
            is_error = "error" in insight or "error" in str(insight).lower()
            error_class = "error" if is_error else ""
            status_text = "ERROR" if is_error else "SUCCESS"
            
            pretty_insight = json.dumps(insight, indent=2)
            content_html += f"""
            <div class="card {error_class}">
                <h3>File: {notebook_name} <span class="status-tag">{status_text}</span></h3>
                <pre>{pretty_insight}</pre>
            </div>
            """
        content_html += '</div>'
    
    full_html = html_template.format(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        content=content_html
    )
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"\n[SUCCESS] Visual report generated: {filename}")

def save_markdown_report(summaries: dict, filename: str = "audit_report.md"):
    """
    Generate a Markdown report with text wrapping for better readability.
    """
    markdown_content = f"# KMDS Data Helper: Persona Audit Report\n\n"
    markdown_content += f"*Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"

    # Iterate through each tracked Persona
    for persona, notebooks in summaries.items():
        markdown_content += f"## {persona}\n\n"

        # Extract individual notebook findings matching the persona
        for notebook_name, insight in notebooks.items():
            is_error = "error" in insight or "error" in str(insight).lower()
            status_text = "ERROR" if is_error else "SUCCESS"

            pretty_insight = json.dumps(insight, indent=2)
            wrapped_insight = textwrap.fill(pretty_insight, width=80)

            markdown_content += f"### File: {notebook_name}\n"
            markdown_content += f"**Status:** {status_text}\n\n"
            markdown_content += f"```json\n{wrapped_insight}\n```\n\n"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"\n[SUCCESS] Markdown report generated: {filename}")
