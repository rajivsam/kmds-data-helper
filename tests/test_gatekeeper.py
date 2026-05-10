import requests
import pytest

def test_gatekeeper_rejects_fake_path():
    """
    Step 2: Verification.
    Prove the API returns a 400 when given a non-existent path.
    """
    url = "http://localhost:8000/analyze"
    payload = {
        "config_path": "/home/rajiv/this_is_a_fake_directory_12345",
        "output_dir": "./output"
    }
    
    response = requests.post(url, json=payload)
    
    # 400 means the Gatekeeper did its job.
    assert response.status_code == 400
    
    data = response.json()
    # Updated to match your actual engine output
    assert "detail" in data
    assert "failed to initialize" in data["detail"].lower()
