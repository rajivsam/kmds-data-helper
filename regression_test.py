from kmds_data_helper.engine import KMDS_LLM_Engine
from pathlib import Path

def test_engine_paths():
    engine = KMDS_LLM_Engine()
    
    print("\n--- Path Verification ---")
    for feature, path in engine.paths.items():
        exists = path.exists()
        has_files = any(path.glob("*")) if exists else False
        status = "✅" if exists and has_files else "❌"
        print(f"{status} {feature}: {path} (Exists: {exists}, Has Files: {has_files})")

    if not all(engine.active_features.values()):
        print("\n⚠️  Note: Some features are inactive. This is expected if folders are empty.")

if __name__ == "__main__":
    test_engine_paths()
