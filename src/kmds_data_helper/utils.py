import nbformat
import json
from pathlib import Path

def parse_notebook_with_outputs(file_path: str) -> str:
    """
    Parses .ipynb, extracts code/markdown/outputs, and strips out rogue 
    persona template injections using case-insensitive signature checks.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        content = []
        for cell in nb.cells:
            # Extract raw cell source strings
            source_text = cell.source if cell.source else ""
            normalized_source = source_text.lower()
            
            # --- CASE-INSENSITIVE ANTI-HIJACKING STRIP FILTER ---
            # Broad-spectrum evaluation catches 'Statistical analysis' or 'Data Scientist'
            if "persona" in normalized_source and "skills" in normalized_source and "analysis" in normalized_source:
                continue
                
            if cell.cell_type == 'markdown':
                content.append(f"### [MARKDOWN]\n{source_text}")
            elif cell.cell_type == 'code':
                content.append(f"### [CODE]\n{source_text}")
                
                # Capture grounding evidence parameters safely
                for output in cell.get('outputs', []):
                    # Clean lookahead on output blocks to block printed rogue signatures too
                    out_text = output.get('text', '') if 'text' in output else str(output.get('data', {}).get('text/plain', ''))
                    normalized_out = out_text.lower()
                    
                    if "persona" in normalized_out and "skills" in normalized_out:
                        continue
                        
                    if 'text' in output:
                        content.append(f"### [OUTPUT_TEXT]\n{output['text']}")
                    elif 'data' in output and 'text/plain' in output['data']:
                        content.append(f"### [OUTPUT_DATA]\n{output['data']['text/plain']}")
                        
        return "\n\n".join(content)
    except Exception as e:
        return f"Error parsing notebook {file_path}: {str(e)}"

def save_kmds_json(data: dict, output_path: str):
    """Standardized JSON saver for KMDS reports and artifacts."""
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
