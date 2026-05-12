import os
import sys
from pathlib import Path

def check_project_structure(base_path="."):
    """
    STRICT VALIDATION: Confirms existence of the 5 Pillars (notebooks, personas,
    documents, data_dictionary, and data) and identifies file counts.
    """
    # Pillar: (Friendly Name, Required Extension)
    required_pillars = {
        "notebooks": "*.ipynb",
        "personas": "*.yaml",
        "documents": "*.pdf",
        "data_dictionary": "*",
        "data": "*"
    }
    
    base = Path(base_path).resolve()
    missing = []
    found_summary = []

    print(f"\n{'='*50}")
    print(f"🔍 KMDS WORKSPACE PRE-FLIGHT CHECK")
    print(f"Target: {base}")
    print(f"{'='*50}\n")

    for folder, pattern in required_pillars.items():
        path = base / folder
        
        # 1. Existence Check
        if path.exists() and path.is_dir():
            files = list(path.glob(pattern))
            count = len(files)
            
            # Notebooks and Personas are non-negotiable for the engine
            if count == 0 and folder in ["notebooks", "personas"]:
                status = "⚠️  EMPTY"
                missing.append(f"{folder} (needs {pattern} files)")
            else:
                status = "✅ OK"
            
            found_summary.append(f"{status} | {folder:<15} | {count} file(s)")
        else:
            print(f"❌ MISSING | {folder:<15}")
            missing.append(folder)

    # Print Summary
    for line in found_summary:
        print(line)

    if missing:
        print(f"\n{'!'*50}")
        print(f"FAILURE: Workspace incomplete.")
        print(f"Missing or Empty: {', '.join(missing)}")
        print(f"{'!'*50}\n")
        sys.exit(1)
    else:
        print(f"\n🚀 SUCCESS: Workspace is ready for the KMDS Audit Engine.")
        print(f"{'='*50}\n")
        sys.exit(0)

def main():
    # Allows passing a directory as an argument: uv run kmds-check ./other_data
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    check_project_structure(target)

if __name__ == "__main__":
    main()
