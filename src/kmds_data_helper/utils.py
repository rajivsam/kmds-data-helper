import nbformat
import json
from pathlib import Path

def parse_notebook_with_outputs(file_path: str) -> str:
    """
    Parses .ipynb and extracts code, markdown, and text-based outputs.
    This provides the evidence-based 'fuel' for the Modeling DS persona.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        content = []
        for cell in nb.cells:
            if cell.cell_type == 'markdown':
                content.append(f"[MARKDOWN]: {cell.source}")
            elif cell.cell_type == 'code':
                content.append(f"[CODE]: {cell.source}")
                
                # Capture printed outputs, DF heads, and evaluation metrics
                for output in cell.get('outputs', []):
                    if 'text' in output:
                        content.append(f"[OUTPUT]: {output['text']}")
                    elif 'data' in output and 'text/plain' in output['data']:
                        content.append(f"[OUTPUT]: {output['data']['text/plain']}")
                        
        return "\n".join(content)
    except Exception as e:
        return f"Error parsing notebook {file_path}: {str(e)}"

def save_kmds_json(data: dict, output_path: str):
    """Standardized JSON saver for KMDS reports and artifacts."""
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
