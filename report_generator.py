import json
from datetime import datetime

def save_html_report(summaries: dict, filename: str = "audit_report.html"):
    html_template = """
    <html>
    <head>
        <title>KMDS Persona Audit Report</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background: #f0f2f5; color: #333; }}
            .container {{ max-width: 1000px; margin: auto; }}
            .card {{ background: white; padding: 25px; margin-bottom: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 5px solid #0056b3; }}
            h1 {{ color: #1a1a1a; text-align: center; }}
            h2 {{ color: #0056b3; margin-top: 0; display: flex; justify-content: space-between; align-items: center; }}
            .status-tag {{ font-size: 0.7em; background: #e7f3ff; color: #0056b3; padding: 4px 12px; border-radius: 20px; }}
            pre {{ background: #1e1e1e; color: #dcdcdc; padding: 20px; border-radius: 8px; overflow-x: auto; font-size: 14px; line-height: 1.5; }}
            .meta {{ text-align: center; color: #666; margin-bottom: 40px; font-style: italic; }}
            .error {{ border-left: 5px solid #dc3545; }}
            .error h2 {{ color: #dc3545; }}
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
    
    cards = ""
    for persona, insight in summaries.items():
        is_error = "error" in insight
        error_class = "error" if is_error else ""
        status_text = "ERROR" if is_error else "SUCCESS"
        
        pretty_insight = json.dumps(insight, indent=2)
        cards += f"""
        <div class="card {error_class}">
            <h2>{persona} <span class="status-tag">{status_text}</span></h2>
            <pre>{pretty_insight}</pre>
        </div>
        """
    
    full_html = html_template.format(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        content=cards
    )
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"\n[SUCCESS] Visual report generated: {filename}")
