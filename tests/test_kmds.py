from src.kmds_data_helper.config_manager import KMDSConfigManager
from src.kmds_data_helper.data_processor import KMDSDataProcessor

def test_isolation():
    print("🧪 Testing Path Anchoring & Isolation...")
    cfg = KMDSConfigManager()
    proc = KMDSDataProcessor(cfg)
    
    # Check paths
    print(f"Base Directory: {cfg.root}")
    print(f"Output Path: {cfg.paths['output']}")
    
    # Regression: Check Ground Truth
    truth = proc.get_ground_truth()
    sources = [item['source'] for item in truth if 'columns' in item]
    
    print(f"Detected Data Sources: {sources}")
    # Verify no file from the /output path leaked into the truth
    for s in sources:
        if "kmds_summary" in s:
            print("❌ REGRESSION FAILED: Output isolation leaked.")
            return
    print("✅ REGRESSION PASSED: Isolation logic is intact.")

if __name__ == "__main__":
    test_isolation()
