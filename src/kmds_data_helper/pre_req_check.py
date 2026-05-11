import os
import sys

def check_project_structure(base_path="."):
    """Verifies that the target workspace meets KMDS requirements."""
    required_dirs = ["notebooks", "data", "output", "documents"]
    missing = []

    print(f"--- KMDS Pre-requisite Check ---")
    print(f"Target Path: {os.path.abspath(base_path)}\n")

    for folder in required_dirs:
        path = os.path.join(base_path, folder)
        if os.path.isdir(path):
            print(f"[OK] Found: {folder}/")
        else:
            print(f"[MISSING] {folder}/")
            missing.append(folder)

    if missing:
        print(f"\nERROR: Project structure incomplete. Missing: {', '.join(missing)}")
        sys.exit(1)
    else:
        print(f"\nSUCCESS: Workspace follows KMDS standards.")
        sys.exit(0)

if __name__ == "__main__":
    # Can pass a path as an argument or check current dir
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    check_project_structure(target)
